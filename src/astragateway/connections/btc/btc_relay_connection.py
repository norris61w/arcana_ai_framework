from typing import TYPE_CHECKING

from astracommon.messages.astra.tx_message import TxMessage
from astracommon.network.abstract_socket_connection_protocol import AbstractSocketConnectionProtocol
from astracommon.utils.blockchain_utils.btc import btc_common_utils
from astragateway.connections.abstract_relay_connection import AbstractRelayConnection
from astrautils import logging
from astragateway import log_messages

if TYPE_CHECKING:
    from astragateway.connections.abstract_gateway_node import AbstractGatewayNode

logger = logging.get_logger(__name__)


class BtcRelayConnection(AbstractRelayConnection):

    def __init__(self, sock: AbstractSocketConnectionProtocol, node: "AbstractGatewayNode"):
        super(BtcRelayConnection, self).__init__(sock, node)

    def msg_tx(self, msg):
        if msg.tx_val() != TxMessage.EMPTY_TX_VAL:
            hash_val = btc_common_utils.get_txid(msg.tx_val())

            if hash_val != msg.tx_hash():
                self.log_error(log_messages.MALFORMED_TX_FROM_RELAY, hash_val, msg.tx_hash())
                return

        super(BtcRelayConnection, self).msg_tx(msg)
