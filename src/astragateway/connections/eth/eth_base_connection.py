from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from astracommon.utils.blockchain_utils.eth import eth_common_constants

from astracommon.messages.abstract_message import AbstractMessage
from astracommon.messages.abstract_message_factory import AbstractMessageFactory
from astracommon.network.abstract_socket_connection_protocol import AbstractSocketConnectionProtocol
from astragateway.messages.eth.protocol.eth_protocol_message_factory import EthProtocolMessageFactory
from astragateway.messages.eth.protocol.eth_protocol_message_type import EthProtocolMessageType
from astragateway.messages.eth.protocol.ping_eth_protocol_message import PingEthProtocolMessage
from astragateway.utils.eth.rlpx_cipher import RLPxCipher
from astrautils import logging

from astragateway.connections.abstract_gateway_blockchain_connection import AbstractGatewayBlockchainConnection

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from astragateway.connections.eth.eth_gateway_node import EthGatewayNode

logger = logging.get_logger(__name__)


class EthBaseConnection(AbstractGatewayBlockchainConnection["EthGatewayNode"], ABC):
    is_handshake_initiator: bool
    rlpx_cipher: RLPxCipher

    def __init__(self, sock: AbstractSocketConnectionProtocol, node: "EthGatewayNode"):
        private_key = node.get_private_key()
        public_key = self.connection_public_key(sock, node)
        self.is_handshake_initiator = public_key is not None
        self.rlpx_cipher = RLPxCipher(
            self.is_handshake_initiator, private_key, public_key
        )
        self.version = eth_common_constants.ETH_PROTOCOL_VERSION
        super().__init__(sock, node)

    @abstractmethod
    def connection_public_key(
        self, sock: AbstractSocketConnectionProtocol, node: "EthGatewayNode"
    ) -> bytes:
        pass

    def connection_message_factory(self) -> AbstractMessageFactory:
        factory = EthProtocolMessageFactory(self.rlpx_cipher)
        if self.is_handshake_initiator:
            factory.set_expected_msg_type(EthProtocolMessageType.AUTH_ACK)
        else:
            factory.set_expected_msg_type(EthProtocolMessageType.AUTH)
        return factory

    def ping_message(self) -> AbstractMessage:
        return PingEthProtocolMessage(None)

    def enqueue_msg(self, msg, prepend=False):
        if not self.is_alive():
            return

        self._log_message(msg.log_level(), "Enqueued message: {}", msg)

        full_message_bytes = bytearray()
        for message_bytes in self.connection_protocol.get_message_bytes(msg):
            full_message_bytes.extend(message_bytes)

        self.enqueue_msg_bytes(full_message_bytes, prepend)

    def is_version_66(self) -> bool:
        return self.version >= 66
