import websockets

from astracommon.rpc.provider.ws_provider import WsProvider
from astracommon.utils import config


class IpcProvider(WsProvider):
    """
    Provider that connects to astragateway's websocket RPC endpoint.
    """

    def __init__(self, ipc_file: str):
        super().__init__(ipc_file)
        self.ipc_path: str = config.get_data_file(ipc_file)

    async def connect_websocket(self) -> websockets.WebSocketClientProtocol:
        return await websockets.unix_connect(self.ipc_path)
