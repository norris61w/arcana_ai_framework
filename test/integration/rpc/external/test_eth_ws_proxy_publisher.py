import asyncio
import blxr_rlp as rlp
import websockets

from typing import Dict, Any
from datetime import date
from unittest.mock import patch, MagicMock

from astracommon import constants
from astracommon.feed.feed import FeedKey
from astracommon.models.node_type import NodeType
from astracommon.models.outbound_peer_model import OutboundPeerModel
from astracommon.rpc.json_rpc_request import JsonRpcRequest
from astracommon.rpc.json_rpc_response import JsonRpcResponse
from astracommon.test_utils import helpers
from astracommon.test_utils.abstract_test_case import AbstractTestCase
from astracommon.test_utils.helpers import async_test
from astracommon.utils import convert
from astracommon.utils.blockchain_utils.eth import crypto_utils
from astracommon.messages.eth.serializers.transaction import Transaction
from astracommon.models.bdn_account_model_base import BdnAccountModelBase
from astracommon.models.bdn_service_model_config_base import BdnServiceModelConfigBase

from astracommon.feed.eth.eth_pending_transaction_feed import EthPendingTransactionFeed
from astracommon.feed.subscriber import Subscriber
from astracommon.feed.new_transaction_feed import RawTransactionFeedEntry
from astragateway.rpc.external.eth_ws_proxy_publisher import EthWsProxyPublisher
from astragateway.testing import gateway_helpers
from astragateway.testing.mocks import mock_eth_messages
from astragateway.testing.mocks.mock_gateway_node import MockGatewayNode


TX_SUB_ID = "newPendingTransactions"
_recover_public_key = crypto_utils.recover_public_key


def tx_to_eth_rpc_json(transaction: Transaction) -> Dict[str, Any]:
    """
    Convert a transaction to Ethereum RPC JSON format.
    """
    payload = transaction.to_json()
    payload["gasPrice"] = payload["gas_price"]
    del payload["gas_price"]
    return payload


class EthWsProxyPublisherTest(AbstractTestCase):
    """
    Unit tests for EthWsProxyPublisher functionality.
    """

    @async_test
    async def setUp(self) -> None:
        """
        Setup the test environment with mock server and EthWsProxyPublisher.
        """
        crypto_utils.recover_public_key = MagicMock(return_value=bytes(32))

        # Setup account model
        account_model = BdnAccountModelBase(
            "account_id",
            "account_name",
            "fake_certificate",
            new_transaction_streaming=BdnServiceModelConfigBase(
                expire_date=date(2999, 1, 1).isoformat()
            ),
        )

        # Setup WebSocket URI and server
        self.eth_ws_port = helpers.get_free_port()
        self.eth_ws_uri = f"ws://127.0.0.1:{self.eth_ws_port}"
        self.eth_ws_server_message_queue = asyncio.Queue()
        await self.start_server()

        # Setup gateway node
        gateway_opts = gateway_helpers.get_gateway_opts(
            8000, eth_ws_uri=self.eth_ws_uri, ws=True
        )
        gateway_opts.set_account_options(account_model)
        self.gateway_node = MockGatewayNode(gateway_opts)
        self.gateway_node.transaction_streamer_peer = OutboundPeerModel(
            "127.0.0.1", 8006, node_type=NodeType.INTERNAL_GATEWAY
        )
        self.gateway_node.feed_manager.register_feed(
            EthPendingTransactionFeed(
                self.gateway_node.alarm_queue, network_num=self.gateway_node.network_num
            )
        )

        # Setup publisher and subscriber
        self.eth_ws_proxy_publisher = EthWsProxyPublisher(
            self.eth_ws_uri,
            self.gateway_node.feed_manager,
            self.gateway_node.get_tx_service(),
            self.gateway_node,
        )
        self.subscriber: Subscriber[RawTransactionFeedEntry] = self.gateway_node.feed_manager.subscribe_to_feed(
            FeedKey(EthPendingTransactionFeed.NAME, network_num=self.gateway_node.network_num), {}
        )
        self.assertIsNotNone(self.subscriber)

        await self.eth_ws_proxy_publisher.start()
        await asyncio.sleep(0.01)

        self.assertEqual(len(self.eth_ws_proxy_publisher.receiving_tasks), 2)
        self.assertEqual(0, self.subscriber.messages.qsize())

        # Sample transactions
        self.sample_transactions = {
            i: mock_eth_messages.get_dummy_transaction(i) for i in range(10)
        }

    async def start_server(self) -> None:
        """
        Start a mock WebSocket server.
        """
        self.eth_test_ws_server = await websockets.serve(
            self.ws_test_serve, constants.LOCALHOST, self.eth_ws_port
        )

    async def ws_test_serve(self, websocket, path):
        """
        Handle incoming and outgoing WebSocket messages.
        """
        async def consumer(ws, _path):
            try:
                async for message in ws:
                    rpc_request = JsonRpcRequest.from_jsons(message)
                    if rpc_request.method_name == "eth_subscribe":
                        await ws.send(
                            JsonRpcResponse(
                                rpc_request.id, str(rpc_request.params[0])
                            ).to_jsons()
                        )
                    elif rpc_request.method_name == "eth_getTransactionByHash":
                        nonce = int(rpc_request.id)
                        await ws.send(
                            JsonRpcResponse(
                                rpc_request.id,
                                tx_to_eth_rpc_json(self.sample_transactions[nonce]),
                            ).to_jsons()
                        )
            except Exception:
                pass  # Server closed, exit

        async def producer(ws, _path):
            try:
                while True:
                    subscription, message = await self.eth_ws_server_message_queue.get()
                    await ws.send(
                        JsonRpcRequest(
                            None,
                            "eth_subscription",
                            {"subscription": subscription, "result": message},
                        ).to_jsons()
                    )
            except Exception:
                pass  # Server closed, exit

        consumer_task = asyncio.create_task(consumer(websocket, path))
        producer_task = asyncio.create_task(producer(websocket, path))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()

    # Other test methods remain as in the original code...

    @async_test
    async def tearDown(self) -> None:
        """
        Cleanup resources after each test.
        """
        await self.eth_ws_proxy_publisher.stop()
        self.eth_test_ws_server.close()
        await self.eth_test_ws_server.wait_closed()
        crypto_utils.recover_public_key = _recover_public_key
