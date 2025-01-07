from asynctest import MagicMock

from astracommon.connections.connection_type import ConnectionType
from astracommon.constants import LOCALHOST
from astracommon.feed.feed import FeedKey
from astracommon.messages.astra.tx_message import TxMessage
from astracommon.models.transaction_flag import TransactionFlag
from astracommon.test_utils import helpers
from astracommon.test_utils.abstract_test_case import AbstractTestCase
from astracommon.test_utils.fixture import eth_fixtures as common_eth_fixtures
from astracommon.test_utils.mocks.mock_node import MockNode
from astracommon.test_utils.mocks.mock_node_ssl_service import MockNodeSSLService
from astracommon.test_utils.mocks.mock_socket_connection import MockSocketConnection
from astragateway.connections.eth.eth_gateway_node import EthGatewayNode
from astragateway.connections.eth.eth_relay_connection import EthRelayConnection
from astracommon.feed.eth.eth_raw_transaction import EthRawTransaction
from astracommon.feed.new_transaction_feed import NewTransactionFeed, FeedSource
from astragateway.messages.eth.protocol.transactions_eth_protocol_message import (
    TransactionsEthProtocolMessage,
)
from astragateway.testing import gateway_helpers
from astragateway.testing.fixture import eth_fixtures
from astragateway.testing.mocks import mock_eth_messages


class EthRelayConnectionTest(AbstractTestCase):
    def setUp(self) -> None:
        pub_key = "a04f30a45aae413d0ca0f219b4dcb7049857bc3f91a6351288cce603a2c9646294a02b987bf6586b370b2c22d74662355677007a14238bb037aedf41c2d08866"
        opts = gateway_helpers.get_gateway_opts(8000, pub_key=pub_key)

        node_ssl_service = MockNodeSSLService(EthGatewayNode.NODE_TYPE, MagicMock())
        self.node = EthGatewayNode(opts, node_ssl_service)
        self.relay_1 = MockNode(helpers.get_common_opts(8000, region="us-east-1"))
        self.relay_connection_1 = helpers.create_connection(
            EthRelayConnection, self.node, node_opts=self.relay_1.opts, file_no=1, ip="1.2.3.4"
        )

        self.relay_2 = MockNode(helpers.get_common_opts(8001, region="eu-west-1"))
        self.relay_connection_2 = helpers.create_connection(
            EthRelayConnection, self.node, node_opts=self.relay_2.opts, file_no=1, ip="1.2.3.5"
        )
        self.node.broadcast = MagicMock()
        self.node.has_active_blockchain_peer = MagicMock(return_value=True)

    def test_publish_new_transaction(self):
        astra_tx_message = self._convert_to_astra_message(eth_fixtures.EIP_155_TXS_MESSAGE)
        astra_tx_message.set_transaction_flag(TransactionFlag.LOCAL_REGION)

        self.node.feed_manager.publish_to_feed = MagicMock()
        self.relay_connection_1.msg_tx(astra_tx_message)

        expected_publication = EthRawTransaction(
            astra_tx_message.tx_hash(),
            astra_tx_message.tx_val(),
            FeedSource.BDN_SOCKET,
            local_region=True,
        )
        self.node.feed_manager.publish_to_feed.assert_called_once_with(
            FeedKey(NewTransactionFeed.NAME, self.node.network_num), expected_publication
        )

    def test_publish_new_tx_from_different_location(self):
        # relay from different region
        astra_tx_message_2 = self._convert_to_astra_message(eth_fixtures.EIP_155_TXS_MESSAGE)
        self.node.feed_manager.publish_to_feed = MagicMock()
        self.relay_connection_2.msg_tx(astra_tx_message_2)

        expected_publication = EthRawTransaction(
            astra_tx_message_2.tx_hash(),
            astra_tx_message_2.tx_val(),
            FeedSource.BDN_SOCKET,
            local_region=False,
        )
        self.node.feed_manager.publish_to_feed.assert_called_once_with(
            FeedKey(NewTransactionFeed.NAME, network_num=self.node.network_num), expected_publication
        )

    def test_publish_new_transaction_low_gas(self):
        astra_tx_message = self._convert_to_astra_message(eth_fixtures.EIP_155_TXS_MESSAGE)

        self.node.feed_manager.publish_to_feed = MagicMock()
        self.node.get_blockchain_network().min_tx_network_fee = (
            common_eth_fixtures.TRANSACTION_EIP_155_GAS_PRICE + 10
        )
        self.relay_connection_1.msg_tx(astra_tx_message)

        self.node.feed_manager.publish_to_feed.assert_not_called()

    def test_transaction_updates_filters_based_on_factor(self):
        self.node.opts.filter_txs_factor = 1
        self._set_bc_connection()

        transactions = [mock_eth_messages.get_dummy_transaction(i, 10) for i in range(100)]
        self.node.on_transactions_in_block(transactions)

        cheap_tx = self._convert_to_astra_message(
            TransactionsEthProtocolMessage(None, [mock_eth_messages.get_dummy_transaction(1, 5)])
        )
        self.relay_connection_1.msg_tx(cheap_tx)
        self.node.broadcast.assert_not_called()

        expensive_tx = self._convert_to_astra_message(
            TransactionsEthProtocolMessage(None, [mock_eth_messages.get_dummy_transaction(1, 15)])
        )
        self.relay_connection_1.msg_tx(expensive_tx)
        self._assert_tx_sent()

    def test_msg_tx_paid_tx(self):
        self.node.opts.filter_txs_factor = 1
        self.node.opts.miner = True
        self._set_bc_connection()

        transactions = [mock_eth_messages.get_dummy_transaction(i, 10) for i in range(100)]
        self.node.on_transactions_in_block(transactions)

        astra_tx_message = self._convert_to_astra_message(eth_fixtures.EIP_155_TXS_MESSAGE)
        self.relay_connection_1.msg_tx(astra_tx_message)
        self.node.broadcast.assert_not_called()

        expensive_tx = self._convert_to_astra_message(
            TransactionsEthProtocolMessage(None, [mock_eth_messages.get_dummy_transaction(1, 15)])
        )
        expensive_tx.set_transaction_flag(TransactionFlag.PAID_TX)
        self.relay_connection_1.msg_tx(expensive_tx)
        self._assert_tx_sent()

    def _convert_to_astra_message(
        self, transactions_eth_msg: TransactionsEthProtocolMessage
    ) -> TxMessage:
        astra_tx_message, _, _ = self.node.message_converter.tx_to_astra_txs(transactions_eth_msg, 5)[0]
        return astra_tx_message

    def _set_bc_connection(self) -> None:
        self.node.on_connection_added(
            MockSocketConnection(1, self.node, ip_address=LOCALHOST, port=7000)
        )
        self.assertEqual(
            1,
            len(
                list(
                    self.node.connection_pool.get_by_connection_types(
                        [ConnectionType.BLOCKCHAIN_NODE]
                    )
                )
            ),
        )
        self.assertEqual(1, len(self.node.blockchain_peers))
        blockchain_conn = next(
            iter(
                self.node.connection_pool.get_by_connection_types([ConnectionType.BLOCKCHAIN_NODE])
            )
        )
        self.node.requester.send_threaded_request = MagicMock()
        self.node.on_blockchain_connection_ready(blockchain_conn)
        self.assertIsNone(self.node._blockchain_liveliness_alarm)

    def _assert_tx_sent(self):
        self.node.broadcast.assert_called_once()
        calls = self.node.broadcast.call_args_list

        ((sent_tx_msg,), connection_info) = calls[0]
        self.assertIsInstance(sent_tx_msg, TransactionsEthProtocolMessage)
        connection_types = connection_info["connection_types"]
        self.assertEqual(len(connection_types), 1)
        connection_type = connection_types[0]
        self.assertEqual(connection_type, ConnectionType.BLOCKCHAIN_NODE)
