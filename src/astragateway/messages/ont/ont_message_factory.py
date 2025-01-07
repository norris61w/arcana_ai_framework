from typing import Type

from astracommon.messages.abstract_message import AbstractMessage
from astracommon.messages.abstract_message_factory import AbstractMessageFactory
from astragateway.messages.ont.addr_ont_message import AddrOntMessage
from astragateway.messages.ont.block_ont_message import BlockOntMessage
from astragateway.messages.ont.consensus_ont_message import OntConsensusMessage
from astragateway.messages.ont.get_addr_ont_message import GetAddrOntMessage
from astragateway.messages.ont.get_blocks_ont_message import GetBlocksOntMessage
from astragateway.messages.ont.get_data_ont_message import GetDataOntMessage
from astragateway.messages.ont.get_headers_ont_message import GetHeadersOntMessage
from astragateway.messages.ont.headers_ont_message import HeadersOntMessage
from astragateway.messages.ont.inventory_ont_message import InvOntMessage
from astragateway.messages.ont.notfound_ont_message import NotFoundOntMessage
from astragateway.messages.ont.ont_message import OntMessage
from astragateway.messages.ont.ont_message_type import OntMessageType
from astragateway.messages.ont.ping_ont_message import PingOntMessage
from astragateway.messages.ont.pong_ont_message import PongOntMessage
from astragateway.messages.ont.tx_ont_message import TxOntMessage
from astragateway.messages.ont.ver_ack_ont_message import VerAckOntMessage
from astragateway.messages.ont.version_ont_message import VersionOntMessage


class _OntMessageFactory(AbstractMessageFactory):
    _MESSAGE_TYPE_MAPPING = {
        OntMessageType.VERSION: VersionOntMessage,
        OntMessageType.VERACK: VerAckOntMessage,
        OntMessageType.GET_ADDRESS: GetAddrOntMessage,
        OntMessageType.ADDRESS: AddrOntMessage,
        OntMessageType.PING: PingOntMessage,
        OntMessageType.PONG: PongOntMessage,
        OntMessageType.CONSENSUS: OntConsensusMessage,
        OntMessageType.INVENTORY: InvOntMessage,
        OntMessageType.GET_DATA: GetDataOntMessage,
        OntMessageType.GET_HEADERS: GetHeadersOntMessage,
        OntMessageType.GET_BLOCKS: GetBlocksOntMessage,
        OntMessageType.BLOCK: BlockOntMessage,
        OntMessageType.HEADERS: HeadersOntMessage,
        OntMessageType.TRANSACTIONS: TxOntMessage,
        OntMessageType.NOT_FOUND: NotFoundOntMessage
    }

    def __init__(self):
        super(_OntMessageFactory, self).__init__()
        self.message_type_mapping = self._MESSAGE_TYPE_MAPPING

    def get_base_message_type(self) -> Type[AbstractMessage]:
        return OntMessage


ont_message_factory = _OntMessageFactory()
