from aiohttp import ClientSession

from astracommon import constants
from astracommon.rpc import rpc_constants
from astracommon.rpc.astra_json_rpc_request import BxJsonRpcRequest
from astracommon.rpc.json_rpc_response import JsonRpcResponse
from astracommon.rpc.rpc_constants import ContentType
from astracommon.test_utils import helpers
from astracommon.test_utils.helpers import async_test
from astragateway.gateway_opts import GatewayOpts
from astragateway.rpc.https.gateway_http_rpc_server import GatewayHttpRpcServer
from astragateway.testing import gateway_helpers
from astragateway.testing.abstract_gateway_rpc_integration_test import \
    AbstractGatewayRpcIntegrationTest


class GatewayRpcServerTest(AbstractGatewayRpcIntegrationTest):
    @async_test
    async def setUp(self) -> None:
        self.rpc_port = helpers.get_free_port()
        self.rpc_url = f"http://{constants.LOCALHOST}:{self.rpc_port}"
        await super().setUp()
        self.rpc_server = GatewayHttpRpcServer(self.gateway_node)
        await self.rpc_server.start()

    def get_gateway_opts(self) -> GatewayOpts:
        super().get_gateway_opts()
        return gateway_helpers.get_gateway_opts(
            8000, rpc_port=self.rpc_port, account_model=self._account_model, blockchain_protocol="Ethereum")

    async def request(self, req: BxJsonRpcRequest):
        headers = {
            rpc_constants.CONTENT_TYPE_HEADER_KEY: ContentType.JSON.value
        }

        async with ClientSession() as session:
            async with session.post(
                self.rpc_url,
                data=req.to_jsons(),
                headers=headers
            ) as response:
                return JsonRpcResponse.from_json(await response.json())

    @async_test
    async def tearDown(self) -> None:
        await self.rpc_server.stop()
