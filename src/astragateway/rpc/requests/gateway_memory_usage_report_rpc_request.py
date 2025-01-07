from typing import TYPE_CHECKING

from astracommon.rpc.json_rpc_response import JsonRpcResponse
from astracommon.rpc.requests.abstract_rpc_request import AbstractRpcRequest

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    # pylint: disable=ungrouped-imports,cyclic-import
    from astragateway.connections.abstract_gateway_node import AbstractGatewayNode


class GatewayMemoryUsageRpcRequest(AbstractRpcRequest["AbstractGatewayNode"]):
    help = {
        "params": "",
        "description": "instruct gateway node to log detailed memory usage report"
    }

    def validate_params(self) -> None:
        pass

    async def process_request(self) -> JsonRpcResponse:
        node_size = self.node.get_node_memory_size()
        return self.ok(node_size)
