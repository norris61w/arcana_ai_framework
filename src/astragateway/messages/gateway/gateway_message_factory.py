from astracommon.messages.astra.ack_message import AckMessage
from astracommon.messages.astra.astra_message_factory import _BloxrouteMessageFactory
from astracommon.messages.astra.astra_message_type import BloxrouteMessageType
from astracommon.messages.astra.block_holding_message import BlockHoldingMessage
from astracommon.messages.astra.key_message import KeyMessage
from astragateway.messages.gateway.block_propagation_request import BlockPropagationRequestMessage
from astragateway.messages.gateway.block_received_message import BlockReceivedMessage
from astragateway.messages.gateway.blockchain_sync_request_message import BlockchainSyncRequestMessage
from astragateway.messages.gateway.blockchain_sync_response_message import BlockchainSyncResponseMessage
from astragateway.messages.gateway.confirmed_block_message import ConfirmedBlockMessage
from astragateway.messages.gateway.confirmed_tx_message import ConfirmedTxMessage
from astragateway.messages.gateway.gateway_hello_message import GatewayHelloMessage
from astragateway.messages.gateway.gateway_message_type import GatewayMessageType
from astragateway.messages.gateway.request_tx_stream_message import RequestTxStreamMessage


class _GatewayMessageFactory(_BloxrouteMessageFactory):
    _MESSAGE_TYPE_MAPPING = {
        GatewayMessageType.HELLO: GatewayHelloMessage,
        BloxrouteMessageType.ACK: AckMessage,
        GatewayMessageType.BLOCK_RECEIVED: BlockReceivedMessage,
        BloxrouteMessageType.BLOCK_HOLDING: BlockHoldingMessage,
        GatewayMessageType.BLOCK_PROPAGATION_REQUEST: BlockPropagationRequestMessage,
        BloxrouteMessageType.KEY: KeyMessage,
        GatewayMessageType.CONFIRMED_TX: ConfirmedTxMessage,
        GatewayMessageType.REQUEST_TX_STREAM: RequestTxStreamMessage,
        GatewayMessageType.CONFIRMED_BLOCK: ConfirmedBlockMessage,

        # Sync messages are currently unused. See `blockchain_sync_service.py`
        GatewayMessageType.SYNC_REQUEST: BlockchainSyncRequestMessage,
        GatewayMessageType.SYNC_RESPONSE: BlockchainSyncResponseMessage
    }


gateway_message_factory = _GatewayMessageFactory()
