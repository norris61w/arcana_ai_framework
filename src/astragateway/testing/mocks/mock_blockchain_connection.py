# pyre-ignore-all-errors
import datetime
from typing import Tuple, Optional, Union

from astracommon.messages.astra.block_hash_message import BlockHashMessage
from astracommon.messages.astra.tx_message import TxMessage
from astracommon.models.transaction_flag import TransactionFlag
from astracommon.test_utils import helpers
from astracommon.utils import crypto, convert
from astracommon.utils.object_hash import Sha256Hash
from astracommon import constants as common_constants

from astragateway.abstract_message_converter import AbstractMessageConverter, BlockDecompressionResult
from astragateway.connections.abstract_gateway_blockchain_connection import AbstractGatewayBlockchainConnection
from astragateway.utils.block_info import BlockInfo


class MockBlockMessage(BlockHashMessage):
    MESSAGE_TYPE = b"mockblock"


class MockMessageConverter(AbstractMessageConverter):

    PREV_BLOCK = Sha256Hash(helpers.generate_bytearray(crypto.SHA256_HASH_LEN))

    def tx_to_astra_txs(
        self,
        tx_msg,
        network_num: int,
        transaction_flag: Optional[TransactionFlag] = None,
        min_tx_network_fee: int = 0,
        account_id: str = common_constants.DECODED_EMPTY_ACCOUNT_ID
    ):
        return [(tx_msg, tx_msg.tx_hash(), tx_msg.tx_val(), transaction_flag)]

    def astra_tx_to_tx(self, astra_tx_msg):
        return astra_tx_msg

    def block_to_astra_block(
        self, block_msg, tx_service, enable_block_compression: bool, min_tx_age_seconds: float
    ) -> Tuple[memoryview, BlockInfo]:
        return block_msg.rawbytes(), \
               BlockInfo(convert.bytes_to_hex(self.PREV_BLOCK.binary), [], datetime.datetime.utcnow(),
                         datetime.datetime.utcnow(), 0, 0, None, None, 0, 0, 0, [])

    def astra_block_to_block(self, astra_block_msg, tx_service) -> BlockDecompressionResult:
        block_message = MockBlockMessage(buf=astra_block_msg)
        return BlockDecompressionResult(block_message, block_message.block_hash(), [], [])

    def bdn_tx_to_astra_tx(
        self,
        raw_tx: Union[bytes, bytearray, memoryview],
        network_num: int,
        transaction_flag: Optional[TransactionFlag] = None,
        account_id: str = common_constants.DECODED_EMPTY_ACCOUNT_ID
    ) -> TxMessage:
        return TxMessage(
            Sha256Hash(crypto.double_sha256(raw_tx)),
            network_num,
            tx_val=raw_tx,
            transaction_flag=transaction_flag,
            account_id=account_id
        )


class MockBlockchainConnection(AbstractGatewayBlockchainConnection):
    def __init__(self, sock, node):
        super(MockBlockchainConnection, self).__init__(sock, node)
