import time
from abc import abstractmethod
from datetime import datetime
from typing import Optional, List, Tuple, Union

from astracommon.messages.astra.tx_message import TxMessage
from astracommon.models.transaction_flag import TransactionFlag
from astracommon.utils import crypto, convert
from astracommon.utils.blockchain_utils.bdn_tx_to_astra_tx import bdn_tx_to_astra_tx
from astracommon.utils.object_hash import Sha256Hash
from astracommon import constants as common_constants

from astragateway import ont_constants
from astragateway.abstract_message_converter import AbstractMessageConverter, BlockDecompressionResult
from astragateway.messages.ont.block_ont_message import BlockOntMessage
from astragateway.messages.ont.consensus_ont_message import OntConsensusMessage
from astragateway.messages.ont.ont_message import OntMessage
from astragateway.messages.ont.tx_ont_message import TxOntMessage
from astragateway.utils.block_info import BlockInfo


def get_block_info(
        astra_block: memoryview,
        block_hash: Sha256Hash,
        short_ids: List[int],
        decompress_start_datetime: datetime,
        decompress_start_timestamp: float,
        total_tx_count: Optional[int] = None,
        ont_block_msg: Optional[Union[BlockOntMessage, OntConsensusMessage]] = None
) -> BlockInfo:
    if ont_block_msg is not None:
        astra_block_hash = convert.bytes_to_hex(crypto.double_sha256(astra_block))
        compressed_size = len(astra_block)
        prev_block_hash = convert.bytes_to_hex(ont_block_msg.prev_block_hash().binary)
        ont_block_len = len(ont_block_msg.rawbytes())
        compression_rate = 100 - float(compressed_size) / ont_block_len * 100
    else:
        astra_block_hash = None
        compressed_size = None
        prev_block_hash = None
        ont_block_len = None
        compression_rate = None
    return BlockInfo(
        block_hash,
        short_ids,
        decompress_start_datetime,
        datetime.utcnow(),
        (time.time() - decompress_start_timestamp) * 1000,
        total_tx_count,
        astra_block_hash,
        prev_block_hash,
        ont_block_len,
        compressed_size,
        compression_rate,
        []
    )


class AbstractOntMessageConverter(AbstractMessageConverter):

    def __init__(self, ont_magic: int):
        self._ont_magic = ont_magic

    @abstractmethod
    def block_to_astra_block(
        self, block_msg, tx_service, enable_block_compression: bool, min_tx_age_seconds: float
    ) -> Tuple[memoryview, BlockInfo]:
        """
        Pack a blockchain block's transactions into a astra block.
        """
        pass

    @abstractmethod
    def astra_block_to_block(self, astra_block_msg, tx_service) -> BlockDecompressionResult:
        """
        Uncompresses a astra_block from a broadcast astra_block message and converts to a raw ONT astra_block.

        astra_block must be a memoryview, since memoryview[offset] returns a bytearray, while bytearray[offset] returns
        a byte.
        """
        pass

    # pyre-fixme[14]: `astra_tx_to_tx` overrides method defined in
    #  `AbstractMessageConverter` inconsistently.
    def astra_tx_to_tx(self, tx_msg: TxMessage):
        # pyre-fixme[6]: Expected `bytes` for 1st param but got `memoryview`.
        buf = bytearray(ont_constants.ONT_HDR_COMMON_OFF) + tx_msg.tx_val()
        raw_ont_tx_msg = OntMessage(self._ont_magic, TxOntMessage.MESSAGE_TYPE, len(tx_msg.tx_val()), buf)
        ont_tx_msg = TxOntMessage(buf=raw_ont_tx_msg.buf)

        return ont_tx_msg

    def tx_to_astra_txs(
        self,
        tx_msg,
        network_num: int,
        transaction_flag: Optional[TransactionFlag] = None,
        min_tx_network_fee: int = 0,
        account_id: str = common_constants.DECODED_EMPTY_ACCOUNT_ID
    ) -> List[Tuple[TxMessage, Sha256Hash, Union[bytearray, memoryview]]]:
        astra_tx_msg = TxMessage(
            tx_msg.tx_hash(),
            network_num,
            tx_val=tx_msg.tx(),
            transaction_flag=transaction_flag,
            account_id=account_id
        )
        return [(astra_tx_msg, tx_msg.tx_hash(), tx_msg.tx())]

    def bdn_tx_to_astra_tx(
        self,
        raw_tx: Union[bytes, bytearray, memoryview],
        network_num: int,
        transaction_flag: Optional[TransactionFlag] = None,
        account_id: str = common_constants.DECODED_EMPTY_ACCOUNT_ID
    ) -> TxMessage:
        return bdn_tx_to_astra_tx(raw_tx, network_num, transaction_flag, account_id)
