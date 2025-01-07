from typing import TYPE_CHECKING

from astracommon.rpc.json_rpc_response import JsonRpcResponse
from astracommon.rpc.requests.abstract_rpc_request import AbstractRpcRequest
from astracommon.utils import memory_utils
from astracommon.utils.stats import stats_format

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    # pylint: disable=ungrouped-imports,cyclic-import
    from astragateway.connections.abstract_gateway_node import AbstractGatewayNode

TOTAL_MEM_USAGE = "total_mem_usage"
TOTAL_CACHED_TX = "total_cached_transactions"
TOTAL_CACHED_TX_SIZE = "total_cached_transactions_size"


class GatewayMemoryRpcRequest(AbstractRpcRequest["AbstractGatewayNode"]):

    help = {
        "params": "",
        "description": "return gateway node memory information"
    }

    def validate_params(self) -> None:
        pass

    async def process_request(self) -> JsonRpcResponse:
        tx_service = self.node.get_tx_service()
        cache_state = tx_service.get_cache_state_json()
        return self.ok({
            TOTAL_MEM_USAGE: stats_format.byte_count(memory_utils.get_app_memory_usage()),
            TOTAL_CACHED_TX: cache_state["tx_hash_to_contents_len"],
            TOTAL_CACHED_TX_SIZE: stats_format.byte_count(cache_state["total_tx_contents_size"])
        })

