from typing import Optional

from astracommon.utils.object_hash import Sha256Hash
from astragateway.messages.ont.data_ont_message import DataOntMessage
from astragateway.messages.ont.ont_message_type import OntMessageType


class GetBlocksOntMessage(DataOntMessage):
    MESSAGE_TYPE = OntMessageType.GET_BLOCKS

    def __init__(self, magic: Optional[int] = None, length: Optional[int] = None,
                 hash_start: Optional[Sha256Hash] = None, hash_stop: Optional[Sha256Hash] = None,
                 buf: Optional[bytearray] = None):
        # pyre-fixme[6]: Expected
        #  `Optional[astragateway.utils.ont.ont_object_hash.OntObjectHash]` for 3rd param
        #  but got `Optional[Sha256Hash]`.
        super(GetBlocksOntMessage, self).__init__(magic, length, hash_start, hash_stop, self.MESSAGE_TYPE, buf)
