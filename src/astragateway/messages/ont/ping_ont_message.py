import struct
from typing import Optional

from astragateway import ont_constants
from astragateway.messages.ont.ont_message import OntMessage
from astragateway.messages.ont.ont_message_type import OntMessageType
from astrautils.logging import LogLevel


class PingOntMessage(OntMessage):
    MESSAGE_TYPE = OntMessageType.PING

    def __init__(self, magic: Optional[int] = None, buf: Optional[bytearray] = None, height: Optional[int] = 0):
        if buf is None:
            buf = bytearray(ont_constants.ONT_HDR_COMMON_OFF + ont_constants.ONT_LONG_LONG_LEN)
            self.buf = buf

            off = ont_constants.ONT_HDR_COMMON_OFF
            struct.pack_into("<Q", buf, off, height)
            off += ont_constants.ONT_LONG_LONG_LEN

            super().__init__(magic, self.MESSAGE_TYPE, off - ont_constants.ONT_HDR_COMMON_OFF, buf)

        else:
            self.buf = buf
            self._memoryview = memoryview(buf)
            self._magic = self._command = self._payload_len = self._checksum = None
            self._payload = None
            self._height = height

    def height(self) -> int:
        if self._height == 0:
            if len(self.buf) == ont_constants.ONT_HDR_COMMON_OFF:
                self._height = -1
            else:
                self._height, = struct.unpack_from("<Q", self.buf, ont_constants.ONT_HDR_COMMON_OFF)

        return self._height
