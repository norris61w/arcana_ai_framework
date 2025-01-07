from astragateway.messages.eth.protocol.eth_protocol_message import EthProtocolMessage
from astragateway.messages.eth.protocol.eth_protocol_message_type import EthProtocolMessageType
from astrautils.logging import LogLevel


class PongEthProtocolMessage(EthProtocolMessage):
    msg_type = EthProtocolMessageType.PONG
