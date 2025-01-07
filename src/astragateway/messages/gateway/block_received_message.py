from astracommon.messages.astra.block_hash_message import BlockHashMessage
from astragateway.messages.gateway.gateway_message_type import GatewayMessageType


class BlockReceivedMessage(BlockHashMessage):
    MESSAGE_TYPE = GatewayMessageType.BLOCK_RECEIVED

    def __repr__(self):
        return "BlockReceivedMessage<block_hash: {}>".format(self.block_hash())
