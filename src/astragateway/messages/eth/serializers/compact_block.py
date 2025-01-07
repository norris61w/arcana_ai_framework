import blxr_rlp as rlp
from astracommon.messages.eth.serializers.block_header import BlockHeader
from astragateway.messages.eth.serializers.short_transaction import ShortTransaction


class CompactBlock(rlp.Serializable):
    fields = [
        ("header", BlockHeader),
        ("transactions", rlp.sedes.CountableList(ShortTransaction)),
        ("uncles", rlp.sedes.CountableList(BlockHeader)),
        ("chain_difficulty", rlp.sedes.big_endian_int),
        ("block_number", rlp.sedes.big_endian_int)
    ]
