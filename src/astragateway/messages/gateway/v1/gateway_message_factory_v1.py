from astracommon.messages.astra.ack_message import AckMessage
from astracommon.messages.astra.astra_message_factory import _BloxrouteMessageFactory
from astracommon.messages.astra.astra_message_type import BloxrouteMessageType
from astragateway.messages.gateway.v1.gateway_hello_message_v1 import GatewayHelloMessageV1
from astragateway.messages.gateway.gateway_message_type import GatewayMessageType


class _GatewayMessageFactoryV1(_BloxrouteMessageFactory):
    _MESSAGE_TYPE_MAPPING = {
        GatewayMessageType.HELLO: GatewayHelloMessageV1,
        BloxrouteMessageType.ACK: AckMessage,
    }


gateway_message_factory_v1 = _GatewayMessageFactoryV1()
