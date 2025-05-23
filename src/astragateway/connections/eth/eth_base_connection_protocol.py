import time
from abc import ABCMeta
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast, Optional, Union, List

from astracommon.connections.connection_type import ConnectionType
from astracommon.messages.eth.serializers.block_header import BlockHeader
from astracommon.utils import convert
from astracommon.utils.object_hash import Sha256Hash
from astragateway import gateway_constants
from astracommon.utils.blockchain_utils.eth import eth_common_constants, eth_common_utils
from astragateway.connections.abstract_blockchain_connection_protocol import AbstractBlockchainConnectionProtocol
from astragateway.messages.eth.protocol.block_bodies_eth_protocol_message import \
    BlockBodiesEthProtocolMessage
from astragateway.messages.eth.protocol.block_bodies_v66_eth_protocol_message import \
    BlockBodiesV66EthProtocolMessage
from astragateway.messages.eth.protocol.block_headers_eth_protocol_message import BlockHeadersEthProtocolMessage
from astragateway.messages.eth.protocol.block_headers_v66_eth_protocol_message import \
    BlockHeadersV66EthProtocolMessage
from astragateway.messages.eth.protocol.disconnect_eth_protocol_message import DisconnectEthProtocolMessage
from astragateway.messages.eth.protocol.eth_protocol_message_factory import EthProtocolMessageFactory
from astragateway.messages.eth.protocol.eth_protocol_message_type import EthProtocolMessageType
from astragateway.messages.eth.protocol.get_block_bodies_eth_protocol_message import \
    GetBlockBodiesEthProtocolMessage
from astragateway.messages.eth.protocol.get_block_bodies_v66_eth_protocol_message import \
    GetBlockBodiesV66EthProtocolMessage
from astragateway.messages.eth.protocol.get_block_headers_eth_protocol_message import \
    GetBlockHeadersEthProtocolMessage
from astragateway.messages.eth.protocol.get_block_headers_v66_eth_protocol_message import \
    GetBlockHeadersV66EthProtocolMessage
from astragateway.messages.eth.protocol.get_pooled_transactions_eth_protocol_message import \
    GetPooledTransactionsEthProtocolMessage
from astragateway.messages.eth.protocol.get_pooled_transactions_v66_eth_protocol_message import \
    GetPooledTransactionsV66EthProtocolMessage
from astragateway.messages.eth.protocol.hello_eth_protocol_message import HelloEthProtocolMessage
from astragateway.messages.eth.protocol.pong_eth_protocol_message import PongEthProtocolMessage
from astragateway.messages.eth.protocol.raw_eth_protocol_message import RawEthProtocolMessage
from astragateway.messages.eth.protocol.status_eth_protocol_message import StatusEthProtocolMessage
from astragateway.messages.eth.protocol.status_eth_protocol_message_v63 import StatusEthProtocolMessageV63
from astragateway.messages.eth.serializers.transient_block_body import TransientBlockBody
from astragateway.utils.eth import frame_utils
from astragateway.utils.eth.rlpx_cipher import RLPxCipher
from astragateway.utils.stats.eth.eth_gateway_stats_service import eth_gateway_stats_service
from astrautils import logging

if TYPE_CHECKING:
    from astragateway.connections.eth.eth_gateway_node import EthGatewayNode
    from astragateway.connections.eth.eth_base_connection import EthBaseConnection

logger = logging.get_logger(__name__)


@dataclass
class EthConnectionProtocolStatus:
    auth_message_sent: bool = False
    auth_message_received: bool = False
    auth_ack_message_sent: bool = False
    auth_ack_message_received: bool = False
    hello_message_sent: bool = False
    hello_message_received: bool = False
    status_message_sent: bool = False
    status_message_received: bool = False
    disconnect_message_received: bool = False
    disconnect_reason: Optional[int] = None


class EthBaseConnectionProtocol(AbstractBlockchainConnectionProtocol, metaclass=ABCMeta):
    node: "EthGatewayNode"
    connection: "EthBaseConnection"

    def __init__(self, connection, is_handshake_initiator, rlpx_cipher: RLPxCipher):
        super(EthBaseConnectionProtocol, self).__init__(
            connection,
            block_cleanup_poll_interval_s=eth_common_constants.BLOCK_CLEANUP_NODE_BLOCK_LIST_POLL_INTERVAL_S
        )

        self.node = cast("EthGatewayNode", connection.node)
        self.connection = cast("EthBaseConnection", connection)
        self.rlpx_cipher = rlpx_cipher
        self.connection_status = EthConnectionProtocolStatus()

        self._last_ping_pong_time: Optional[float] = None
        self._handshake_complete = False

        connection.hello_messages = [
            EthProtocolMessageType.AUTH,
            EthProtocolMessageType.AUTH_ACK,
            EthProtocolMessageType.HELLO,
            EthProtocolMessageType.STATUS,
            # Ethereum Parity sends PING message before handshake is completed
            EthProtocolMessageType.PING,
            EthProtocolMessageType.DISCONNECT
        ]

        connection.message_handlers = {
            EthProtocolMessageType.AUTH: self.msg_auth,
            EthProtocolMessageType.AUTH_ACK: self.msg_auth_ack,
            EthProtocolMessageType.HELLO: self.msg_hello,
            EthProtocolMessageType.STATUS: self.msg_status,
            EthProtocolMessageType.DISCONNECT: self.msg_disconnect,
            EthProtocolMessageType.PING: self.msg_ping,
            EthProtocolMessageType.PONG: self.msg_pong,
            EthProtocolMessageType.GET_BLOCK_HEADERS: self.msg_get_block_headers
        }
        connection.pong_message = PongEthProtocolMessage(None)

        self._waiting_checkpoint_headers_request = True

        if is_handshake_initiator:
            self.connection.log_trace("Public key is known. Starting handshake.")
            self._enqueue_auth_message()
        else:
            self.connection.log_trace("Public key is unknown. Waiting for handshake request.")
            self.node.alarm_queue.register_alarm(eth_common_constants.HANDSHAKE_TIMEOUT_SEC, self._handshake_timeout)

    def msg_auth(self, msg):
        self.connection.log_trace("Beginning processing of auth message.")
        self.connection_status.auth_message_received = True
        msg_bytes = msg.rawbytes()
        decrypted_auth_msg, size = self.rlpx_cipher.decrypt_auth_message(bytes(msg_bytes))
        if decrypted_auth_msg is None:
            self.connection.log_trace("Auth message is incomplete. Waiting for more bytes.")
            return

        self.rlpx_cipher.parse_auth_message(decrypted_auth_msg)

        self._enqueue_auth_ack_message()
        self._finalize_handshake()
        self._enqueue_hello_message()
        self.connection.message_factory.reset_expected_msg_type()

    def msg_auth_ack(self, msg):
        self.connection.log_trace("Beginning processing of auth ack message.")
        self.connection_status.auth_ack_message_received = True
        auth_ack_msg_bytes = msg.rawbytes()
        self.rlpx_cipher.decrypt_auth_ack_message(bytes(auth_ack_msg_bytes))
        self._finalize_handshake()
        self._enqueue_hello_message()
        self.connection.message_factory.reset_expected_msg_type()

    def msg_ping(self, msg):
        self.connection.msg_ping(msg)
        self._last_ping_pong_time = time.time()

    def msg_pong(self, msg):
        self.connection.msg_pong(msg)
        self._last_ping_pong_time = time.time()

    def msg_hello(self, msg: HelloEthProtocolMessage):
        client_version_string = msg.get_client_version_string()
        version = msg.get_version()
        self.connection.log_info("Exchanging handshake messages with blockchain node {}, with version field {}.",
                                 client_version_string, version)
        self.connection_status.hello_message_received = True

    def msg_status(self, msg: Union[StatusEthProtocolMessage, StatusEthProtocolMessageV63]):
        self.connection.log_trace("Status message received.")
        try:
            protocol_version = msg.get_eth_version()
        except Exception:
            status_msg = StatusEthProtocolMessageV63(msg.rawbytes())
            protocol_version = status_msg.get_eth_version()
        else:
            status_msg = msg

        self.connection.log_info("Status message received. Version: {}", protocol_version)
        message_factory = cast(EthProtocolMessageFactory, self.connection.message_factory)
        message_factory.set_mappings_for_version(protocol_version)
        self.connection.version = protocol_version

        self.connection_status.status_message_received = True

        for peer in self.node.blockchain_peers:
            if self.node.is_blockchain_peer(self.connection.peer_ip, self.connection.peer_port):
                peer.connection_established = True

        chain_difficulty_from_status_msg = status_msg.get_chain_difficulty()
        chain_difficulty = int(self.node.opts.chain_difficulty, 16)
        fork_id = status_msg.get_fork_id()
        if isinstance(chain_difficulty_from_status_msg, int) and chain_difficulty_from_status_msg > chain_difficulty:
            chain_difficulty = chain_difficulty_from_status_msg
        self._enqueue_status_message(chain_difficulty, fork_id, protocol_version)

    def msg_disconnect(self, msg):
        self.connection_status.disconnect_message_received = True
        self.connection_status.disconnect_reason = msg.get_reason()

        self.connection.log_debug("Disconnect message was received from the blockchain node. Disconnect reason '{0}'.",
                                  self.connection_status.disconnect_reason)
        self.connection.mark_for_close()

    def msg_get_block_headers(self, msg):
        self.connection.log_trace("Replying with empty headers message to the get headers request")

        request_id: Optional[int] = None
        if isinstance(msg, GetBlockHeadersV66EthProtocolMessage):
            request_id = msg.get_request_id()

        self.send_block_headers([], request_id)
        self._waiting_checkpoint_headers_request = False

    def request_block_headers(self, start_hash: Sha256Hash, amount: int, skip: int, reverse: int) -> None:
        # difference between v65 and v66:
        # https://github.com/ethereum/devp2p/blob/master/caps/eth.md#getblockheaders-0x03
        request = GetBlockHeadersEthProtocolMessage(None, start_hash.binary, amount, skip, reverse)
        if self.connection.is_version_66():
            request = GetBlockHeadersV66EthProtocolMessage(
                None, eth_common_utils.generate_message_request_id(), request
            )

        self.connection.enqueue_msg(request)

    def request_block_bodies(self, block_hashes: List[Sha256Hash]) -> None:
        if self.connection.is_version_66():
            block_request_message = GetBlockBodiesV66EthProtocolMessage(
                None, eth_common_utils.generate_message_request_id(), [block_hash.binary for block_hash in block_hashes]
            )
        else:
            block_request_message = GetBlockBodiesEthProtocolMessage(
                None, [block_hash.binary for block_hash in block_hashes]
            )

        self.connection.enqueue_msg(block_request_message)

    def request_transactions(self, tx_hashes: List[Sha256Hash]) -> None:
        if self.connection.is_version_66():
            request = GetPooledTransactionsV66EthProtocolMessage(
                None, eth_common_utils.generate_message_request_id(), [tx_hash.binary for tx_hash in tx_hashes]
            )
        else:
            request = GetPooledTransactionsEthProtocolMessage(
                None, [tx_hash.binary for tx_hash in tx_hashes]
            )

        self.connection.enqueue_msg(request)

    def send_block_headers(self, headers: List[BlockHeader], request_id: Optional[int]) -> None:
        if self.connection.is_version_66():
            if request_id is None:
                raise ValueError("cannot respond with block headers for protocol 66 message without request ID")
            block_headers_msg = BlockHeadersV66EthProtocolMessage(None, request_id, headers)
        else:
            block_headers_msg = BlockHeadersEthProtocolMessage(None, headers)

        self.connection.enqueue_msg(block_headers_msg)

    def send_block_bodies(self, bodies: List[TransientBlockBody], request_id: Optional[int]) -> None:
        # difference between v65 and v66:
        # https://github.com/ethereum/devp2p/blob/master/caps/eth.md#getblockheaders-0x03
        block_bodies_msg = BlockBodiesEthProtocolMessage(None, bodies)

        if self.connection.is_version_66():
            if request_id is None:
                raise ValueError("cannot respond with block bodies for protocol 66 message without request ID")
            block_bodies_msg = BlockBodiesV66EthProtocolMessage(None, request_id, bodies)

        self.connection.enqueue_msg(block_bodies_msg)

    def get_message_bytes(self, msg):
        if isinstance(msg, RawEthProtocolMessage):
            yield msg.rawbytes()
        else:
            serialization_start_time = time.time()
            frames = frame_utils.get_frames(msg.msg_type,
                                            msg.rawbytes(),
                                            eth_common_constants.DEFAULT_FRAME_PROTOCOL_ID,
                                            eth_common_constants.DEFAULT_FRAME_SIZE)
            eth_gateway_stats_service.log_serialized_message(time.time() - serialization_start_time)

            assert frames
            self.connection.log_trace("Broke message into {} frames", len(frames))

            encryption_start_time = time.time()
            for frame in frames:
                yield self.rlpx_cipher.encrypt_frame(frame)
            eth_gateway_stats_service.log_encrypted_message(time.time() - encryption_start_time)

    def _enqueue_auth_message(self):
        auth_msg_bytes = self._get_auth_msg_bytes()
        self.connection.log_debug("Enqueued auth bytes.")
        self.connection.enqueue_msg_bytes(auth_msg_bytes)
        self.connection_status.auth_message_sent = True

    def _enqueue_auth_ack_message(self):
        auth_ack_msg_bytes = self._get_auth_ack_msg_bytes()
        self.connection.log_debug("Enqueued auth ack bytes.")
        self.connection.enqueue_msg_bytes(auth_ack_msg_bytes)
        self.connection_status.auth_ack_message_sent = True

    def _get_eth_protocol_version(self) -> int:
        for peer in self.node.blockchain_peers:
            if self.node.is_blockchain_peer(self.connection.peer_ip, self.connection.peer_port):
                return peer.blockchain_protocol_version
        return eth_common_constants.ETH_PROTOCOL_VERSION

    def _enqueue_hello_message(self):
        public_key = self.node.get_public_key()
        eth_protocol_version = eth_common_constants.ETH_PROTOCOL_VERSION
        if self.connection.CONNECTION_TYPE == ConnectionType.BLOCKCHAIN_NODE:
            eth_protocol_version = self._get_eth_protocol_version()
        elif self.connection.CONNECTION_TYPE == ConnectionType.REMOTE_BLOCKCHAIN_NODE:
            eth_protocol_version = self.node.remote_blockchain_protocol_version

        hello_msg = HelloEthProtocolMessage(
            None,
            eth_common_constants.P2P_PROTOCOL_VERSION,
            f"{gateway_constants.GATEWAY_PEER_NAME} {self.node.opts.source_version}".encode("utf-8"),
            ((b"eth", eth_protocol_version),),
            self.connection.external_port,
            public_key
        )
        self.connection.enqueue_msg(hello_msg)
        self.connection_status.hello_message_sent = True

    def _enqueue_status_message(self, chain_difficulty: int, fork_id, protocol_version: int):
        network_id = self.node.opts.network_id
        chain_head_hash = convert.hex_to_bytes(self.node.opts.genesis_hash)
        genesis_hash = chain_head_hash

        if protocol_version == 63:
            status_msg = StatusEthProtocolMessageV63(
                None,
                protocol_version,
                network_id,
                chain_difficulty,
                chain_head_hash,
                genesis_hash,
            )
        else:
            status_msg = StatusEthProtocolMessage(
                None,
                protocol_version,
                network_id,
                chain_difficulty,
                chain_head_hash,
                genesis_hash,
                fork_id
            )

        self.connection.enqueue_msg(status_msg)
        self.connection_status.status_message_sent = True

    def _enqueue_disconnect_message(self, disconnect_reason):
        disconnect_msg = DisconnectEthProtocolMessage(None, [disconnect_reason])
        self.connection.enqueue_msg(disconnect_msg)

    def _get_auth_msg_bytes(self):
        auth_msg_bytes = self.rlpx_cipher.create_auth_message()
        auth_msg_bytes_encrypted = self.rlpx_cipher.encrypt_auth_message(auth_msg_bytes)

        return bytearray(auth_msg_bytes_encrypted)

    def _get_auth_ack_msg_bytes(self):
        auth_ack_msg_bytes = self.rlpx_cipher.create_auth_ack_message()
        auth_ack_msg_bytes_encrypted = self.rlpx_cipher.encrypt_auth_ack_message(auth_ack_msg_bytes)

        return bytearray(auth_ack_msg_bytes_encrypted)

    def _finalize_handshake(self):
        self._handshake_complete = True

        self.connection.log_trace("Setting up cipher.")
        self.rlpx_cipher.setup_cipher()

        self._last_ping_pong_time = time.time()
        self.node.alarm_queue.register_alarm(eth_common_constants.PING_PONG_INTERVAL_SEC, self._ping_timeout)

    def _handshake_timeout(self):
        if not self._handshake_complete:
            self.connection.log_debug("Handshake was not completed within defined timeout. Closing connection.")
            self.connection.mark_for_close()
        else:
            self.connection.log_trace("Handshake completed within defined timeout.")
        return 0

    def _ping_timeout(self) -> float:
        if not self.connection.is_alive():
            return 0

        last_ping_pong_time = self._last_ping_pong_time
        assert last_ping_pong_time is not None
        time_since_last_ping_pong = time.time() - last_ping_pong_time
        self.connection.log_trace("Ping timeout: {} seconds since last ping / pong received from node.",
                                  time_since_last_ping_pong)

        if time_since_last_ping_pong > eth_common_constants.PING_PONG_TIMEOUT_SEC:
            self.connection.log_debug("Node has not replied with ping / pong for {} seconds, more than {} limit."
                                      "Disconnecting", time_since_last_ping_pong, eth_common_constants.PING_PONG_TIMEOUT_SEC)
            self._enqueue_disconnect_message(eth_common_constants.DISCONNECT_REASON_TIMEOUT)
            self.node.alarm_queue.register_alarm(eth_common_constants.DISCONNECT_DELAY_SEC, self.connection.mark_for_close)

        return 0
