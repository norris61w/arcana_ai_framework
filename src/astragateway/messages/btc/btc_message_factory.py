from typing import Type

from astracommon.messages.abstract_message import AbstractMessage
from astracommon.messages.abstract_message_factory import AbstractMessageFactory
from astragateway.messages.btc.addr_btc_message import AddrBtcMessage
from astragateway.messages.btc.block_btc_message import BlockBtcMessage
from astragateway.messages.btc.block_transactions_btc_message import BlockTransactionsBtcMessage
from astragateway.messages.btc.btc_message import BtcMessage
from astragateway.messages.btc.btc_message_type import BtcMessageType
from astragateway.messages.btc.compact_block_btc_message import CompactBlockBtcMessage
from astragateway.messages.btc.data_btc_message import GetBlocksBtcMessage, GetHeadersBtcMessage
from astragateway.messages.btc.fee_filter_btc_message import FeeFilterBtcMessage
from astragateway.messages.btc.get_addr_btc_message import GetAddrBtcMessage
from astragateway.messages.btc.get_block_transactions_btc_message import GetBlockTransactionsBtcMessage
from astragateway.messages.btc.headers_btc_message import HeadersBtcMessage
from astragateway.messages.btc.inventory_btc_message import GetDataBtcMessage, InvBtcMessage, NotFoundBtcMessage
from astragateway.messages.btc.ping_btc_message import PingBtcMessage
from astragateway.messages.btc.pong_btc_message import PongBtcMessage
from astragateway.messages.btc.reject_btc_message import RejectBtcMessage
from astragateway.messages.btc.send_compact_btc_message import SendCompactBtcMessage
from astragateway.messages.btc.send_headers_btc_message import SendHeadersBtcMessage
from astragateway.messages.btc.tx_btc_message import TxBtcMessage
from astragateway.messages.btc.ver_ack_btc_message import VerAckBtcMessage
from astragateway.messages.btc.version_btc_message import VersionBtcMessage
from astragateway.messages.btc.xversion_btc_message import XversionBtcMessage


class _BtcMessageFactory(AbstractMessageFactory):
    _MESSAGE_TYPE_MAPPING = {
        BtcMessageType.VERSION: VersionBtcMessage,
        BtcMessageType.VERACK: VerAckBtcMessage,
        BtcMessageType.PING: PingBtcMessage,
        BtcMessageType.PONG: PongBtcMessage,
        BtcMessageType.GET_ADDRESS: GetAddrBtcMessage,
        BtcMessageType.ADDRESS: AddrBtcMessage,
        BtcMessageType.INVENTORY: InvBtcMessage,
        BtcMessageType.GET_DATA: GetDataBtcMessage,
        BtcMessageType.NOT_FOUND: NotFoundBtcMessage,
        BtcMessageType.GET_HEADERS: GetHeadersBtcMessage,
        BtcMessageType.GET_BLOCKS: GetBlocksBtcMessage,
        BtcMessageType.TRANSACTIONS: TxBtcMessage,
        BtcMessageType.BLOCK: BlockBtcMessage,
        BtcMessageType.HEADERS: HeadersBtcMessage,
        BtcMessageType.REJECT: RejectBtcMessage,
        BtcMessageType.SEND_HEADERS: SendHeadersBtcMessage,
        BtcMessageType.COMPACT_BLOCK: CompactBlockBtcMessage,
        BtcMessageType.GET_BLOCK_TRANSACTIONS: GetBlockTransactionsBtcMessage,
        BtcMessageType.BLOCK_TRANSACTIONS: BlockTransactionsBtcMessage,
        BtcMessageType.FEE_FILTER: FeeFilterBtcMessage,
        BtcMessageType.SEND_COMPACT: SendCompactBtcMessage,
        BtcMessageType.XVERSION: XversionBtcMessage
    }

    def __init__(self):
        super(_BtcMessageFactory, self).__init__()
        self.message_type_mapping = self._MESSAGE_TYPE_MAPPING

    def get_base_message_type(self) -> Type[AbstractMessage]:
        return BtcMessage


btc_message_factory = _BtcMessageFactory()
