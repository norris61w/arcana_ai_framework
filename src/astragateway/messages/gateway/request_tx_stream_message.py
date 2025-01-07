from typing import Optional

from astracommon import constants
from astracommon.messages.astra.abstract_astra_message import AbstractBloxrouteMessage
from astragateway.messages.gateway.gateway_message_type import GatewayMessageType
from astrautils.logging import LogLevel


class RequestTxStreamMessage(AbstractBloxrouteMessage):

    MESSAGE_TYPE = GatewayMessageType.REQUEST_TX_STREAM

    def __init__(self, buf: Optional[bytearray] = None) -> None:
        if buf is None:
            buf = bytearray(
                AbstractBloxrouteMessage.HEADER_LENGTH
                + constants.CONTROL_FLAGS_LEN
            )

        super().__init__(self.MESSAGE_TYPE, constants.CONTROL_FLAGS_LEN, buf)

    def log_level(self):
        return LogLevel.DEBUG
