import os
from typing import cast, List
from unittest import skip

from astragateway.connections.ont.ont_node_connection import OntNodeConnection
from astragateway.messages.gateway.block_received_message import BlockReceivedMessage
from astragateway.testing import gateway_helpers
from astracommon.test_utils.mocks.mock_node_ssl_service import MockNodeSSLService
from mock import MagicMock

from astracommon.models.transaction_info import TransactionInfo
from astracommon.models.broadcast_message_type import BroadcastMessageType

from astracommon.test_utils.abstract_test_case import AbstractTestCase
from astracommon.connections.connection_type import ConnectionType
from astracommon.constants import DEFAULT_NETWORK_NUM, LOCALHOST
from astracommon.messages.astra.broadcast_message import BroadcastMessage
from astracommon.messages.astra.get_txs_message import GetTxsMessage
from astracommon.messages.astra.key_message import KeyMessage
from astracommon.messages.astra.txs_message import TxsMessage
from astracommon.test_utils import helpers
from astracommon.test_utils.mocks.mock_connection import MockConnection
from astracommon.test_utils.mocks.mock_node import MockNode
from astracommon.test_utils.mocks.mock_socket_connection import MockSocketConnection
from astracommon.utils import crypto, convert
from astracommon.utils.blockchain_utils.ont.ont_object_hash import OntObjectHash
from astracommon.utils.crypto import symmetric_encrypt, SHA256_HASH_LEN
from astracommon.utils.object_hash import Sha256Hash
from astracommon.services.extension_transaction_service import ExtensionTransactionService

from astragateway.connections.ont.ont_gateway_node import OntGatewayNode
from astragateway.connections.ont.ont_node_connection_protocol import OntNodeConnectionProtocol
from astragateway.connections.ont.ont_relay_connection import OntRelayConnection
from astragateway.messages.ont.block_ont_message import BlockOntMessage
import astragateway.messages.ont.ont_message_converter_factory as converter_factory
from astragateway.messages.ont.get_data_ont_message import GetDataOntMessage
from astragateway.messages.ont.inventory_ont_message import InvOntMessage, InventoryOntType
from astragateway.messages.ont.tx_ont_message import TxOntMessage
from astragateway.utils.stats.gateway_transaction_stats_service import gateway_transaction_stats_service


class OntRelayConnectionTest(AbstractTestCase):
    ONT_HASH = OntObjectHash(crypto.double_sha256(b"123"), length=SHA256_HASH_LEN)

    magic = 12345
    version = 111
    TEST_NETWORK_NUM = 12345

    def setUp(self):
        opts = gateway_helpers.get_gateway_opts(8000, include_default_ont_args=True)
        if opts.use_extensions:
            helpers.set_extensions_parallelism(opts.thread_pool_parallelism_degree)
        node_ssl_service = MockNodeSSLService(OntGatewayNode.NODE_TYPE, MagicMock())
        self.gateway_node = OntGatewayNode(opts, node_ssl_service)
        self.gateway_node.opts.has_fully_updated_tx_service = True
        self.gateway_node.opts.is_consensus = False
        self.sut = OntRelayConnection(
            MockSocketConnection(1, node=self.gateway_node, ip_address=LOCALHOST, port=8001), self.gateway_node
            )

        self.node_conn = MockConnection(
            MockSocketConnection(1, self.gateway_node, ip_address=LOCALHOST, port=8002), self.gateway_node
            )
        self.gateway_node.connection_pool.add(1, LOCALHOST, 8002, self.node_conn)
        gateway_helpers.add_blockchain_peer(self.gateway_node, self.node_conn)

        self.node_conn_2 = MockConnection(
            MockSocketConnection(1, self.gateway_node, ip_address=LOCALHOST, port=8003), self.gateway_node
            )
        self.gateway_node.connection_pool.add(1, LOCALHOST, 8003, self.node_conn_2)
        gateway_helpers.add_blockchain_peer(self.gateway_node, self.node_conn_2)
        self.blockchain_connections = [self.node_conn, self.node_conn_2]

        self.gateway_node_sut = OntNodeConnectionProtocol(cast(OntNodeConnection, self.node_conn))
        self.gateway_node.message_converter = converter_factory.create_ont_message_converter(
            12345, self.gateway_node.opts
        )
        self.gateway_node.has_active_blockchain_peer = MagicMock(return_value=True)

        self.gateway_node.broadcast = MagicMock()
        self.node_conn.enqueue_msg = MagicMock()
        self.node_conn_2.enqueue_msg = MagicMock()
        self.sut.enqueue_msg = MagicMock()
        gateway_transaction_stats_service.set_node(self.gateway_node)

    def ont_transactions(self, block: BlockOntMessage = None) -> List[memoryview]:
        txs = block.txns()
        return [TxOntMessage(self.magic, self.version, tx[1:]) for tx in txs]

    def ont_block(self) -> BlockOntMessage:
        return self._get_sample_block()

    def astra_block(self, ont_block=None):
        if ont_block is None:
            ont_block = self.ont_block()
        return bytes(
            self.gateway_node.message_converter.block_to_astra_block(
                ont_block, self.gateway_node.get_tx_service(), True, self.gateway_node.network.min_tx_age_seconds
            )[0]
        )

    def astra_transactions(self, transactions=None, assign_short_ids=False):
        if transactions is None:
            block = self.ont_block()
            transactions = self.ont_transactions(block)

        astra_transactions = []
        for i, transaction in enumerate(transactions):
            transaction = self.gateway_node.message_converter.tx_to_astra_txs(transaction,
                                                                           self.TEST_NETWORK_NUM)[0][0]
            if assign_short_ids:
                transaction._short_id = i + 1  # 0 is null SID
            astra_transactions.append(transaction)
        return astra_transactions

    @skip("Encryption block in Ontology")
    def test_msg_broadcast_wait_for_key(self):
        ont_block = self.ont_block()
        astra_block = self.astra_block(ont_block)

        key, ciphertext = symmetric_encrypt(astra_block)
        block_hash = crypto.double_sha256(ciphertext)
        broadcast_message = BroadcastMessage(Sha256Hash(block_hash), self.TEST_NETWORK_NUM, "",
                                             BroadcastMessageType.BLOCK, True, ciphertext)

        self.sut.msg_broadcast(broadcast_message)

        # handle duplicate messages
        self.sut.msg_broadcast(broadcast_message)
        self.sut.msg_broadcast(broadcast_message)

        self.assertEqual(3, len(self.gateway_node.broadcast.call_args_list))
        for call, conn_type in self.gateway_node.broadcast.call_args_list:
            msg, conn = call
            self.assertTrue(isinstance(msg, BlockReceivedMessage))
        self.gateway_node.broadcast.reset_mock()

        self.assertEqual(1, len(self.gateway_node.in_progress_blocks))

        key_message = KeyMessage(Sha256Hash(block_hash), self.TEST_NETWORK_NUM, "", key)
        self.sut.msg_key(key_message)

        self._assert_block_sent(ont_block)

    def test_msg_broadcast_duplicate_block_with_different_short_id(self):
        # test scenario when first received block is compressed with unknown short ids,
        # but second received block is compressed with known short ids
        ont_block = self.ont_block()
        block_hash = ont_block.block_hash()
        transactions = self.astra_transactions()

        unknown_sid_transaction_service = ExtensionTransactionService(MockNode(
            gateway_helpers.get_gateway_opts(8999)), 0)
        for i, transaction in enumerate(transactions):
            transaction_key = unknown_sid_transaction_service.get_transaction_key(transaction.tx_hash())
            unknown_sid_transaction_service.assign_short_id_by_key(transaction_key, i)
            unknown_sid_transaction_service.set_transaction_contents_by_key(transaction_key, transaction.tx_val())

        unknown_short_id_block = bytes(
            self.gateway_node.message_converter.block_to_astra_block(
                ont_block, unknown_sid_transaction_service, True, self.gateway_node.network.min_tx_age_seconds
            )[0]
        )
        unknown_key, unknown_cipher = symmetric_encrypt(unknown_short_id_block)
        unknown_block_hash = crypto.double_sha256(unknown_cipher)
        unknown_message = BroadcastMessage(Sha256Hash(unknown_block_hash), self.TEST_NETWORK_NUM, "",
                                           BroadcastMessageType.BLOCK, False, bytearray(unknown_short_id_block))
        unknown_key_message = KeyMessage(Sha256Hash(unknown_block_hash), self.TEST_NETWORK_NUM, "", unknown_key)

        local_transaction_service = self.gateway_node.get_tx_service()
        for i, transaction in enumerate(transactions):
            transaction_key = local_transaction_service.get_transaction_key(transaction.tx_hash())
            local_transaction_service.assign_short_id_by_key(transaction_key, i + 20)
            local_transaction_service.set_transaction_contents_by_key(transaction_key, transaction.tx_val())

        known_short_id_block = bytes(
            self.gateway_node.message_converter.block_to_astra_block(
                ont_block, local_transaction_service, True, self.gateway_node.network.min_tx_age_seconds
            )[0]
        )
        known_key, known_cipher = symmetric_encrypt(known_short_id_block)
        known_block_hash = crypto.double_sha256(known_cipher)
        known_message = BroadcastMessage(Sha256Hash(known_block_hash), self.TEST_NETWORK_NUM, "",
                                         BroadcastMessageType.BLOCK, False, bytearray(known_short_id_block))
        known_key_message = KeyMessage(Sha256Hash(known_block_hash), self.TEST_NETWORK_NUM, "", known_key)

        self.sut.msg_broadcast(unknown_message)
        self.sut.msg_key(unknown_key_message)

        block_queuing_service = self.gateway_node.block_queuing_service_manager.get_block_queuing_service(self.node_conn)
        self.assertEqual(1, len(block_queuing_service))
        self.assertEqual(True, block_queuing_service._blocks_waiting_for_recovery[block_hash])
        self.assertEqual(1, len(self.gateway_node.block_recovery_service._block_hash_to_astra_block_hashes))
        self.assertNotIn(block_hash, self.gateway_node.blocks_seen.contents)

        self.sut.msg_broadcast(known_message)
        self.sut.msg_key(known_key_message)
        self.gateway_node_sut.msg_get_data(GetDataOntMessage(self.magic, InventoryOntType.MSG_BLOCK.value, block_hash))

        self.gateway_node.broadcast.assert_called()
        self.assertEqual(0, len(block_queuing_service))
        self.assertEqual(0, len(self.gateway_node.block_recovery_service._block_hash_to_astra_block_hashes))
        self.assertIn(block_hash, self.gateway_node.blocks_seen.contents)

    @skip("Encryption block in Ontology")
    def test_msg_key_wait_for_broadcast(self):
        ont_block = self.ont_block()
        astra_block = self.astra_block(ont_block)

        key, ciphertext = symmetric_encrypt(astra_block)
        block_hash = crypto.double_sha256(ciphertext)

        self.gateway_node.broadcast.assert_not_called()

        key_message = KeyMessage(Sha256Hash(block_hash), self.TEST_NETWORK_NUM, "", key)
        self.sut.msg_key(key_message)

        # handle duplicate broadcasts
        self.sut.msg_key(key_message)
        self.sut.msg_key(key_message)

        self.assertEqual(1, len(self.gateway_node.in_progress_blocks))

        broadcast_message = BroadcastMessage(Sha256Hash(block_hash), self.TEST_NETWORK_NUM, "",
                                             BroadcastMessageType.BLOCK, True, ciphertext)
        self.sut.msg_broadcast(broadcast_message)

        self._assert_block_sent(ont_block)

    def test_msg_tx(self):
        transactions = self.astra_transactions(assign_short_ids=True)
        for transaction in transactions:
            self.sut.msg_tx(transaction)

        for i, transaction in enumerate(transactions):
            transaction_hash = transaction.tx_hash()
            transaction_key = self.gateway_node.get_tx_service().get_transaction_key(transaction_hash)
            self.assertTrue(self.gateway_node.get_tx_service().has_transaction_contents_by_key(transaction_key))
            self.assertTrue(self.gateway_node.get_tx_service().has_transaction_short_id_by_key(transaction_key))
            self.assertEqual(i + 1, self.gateway_node.get_tx_service().get_short_id_by_key(transaction_key))

            stored_hash, stored_content, _ = self.gateway_node.get_tx_service().get_transaction(i + 1)
            self.assertEqual(transaction_hash, stored_hash)
            self.assertEqual(transaction.tx_val(), stored_content)

        self.assertEqual(len(transactions), self.gateway_node.broadcast.call_count)

    def test_msg_tx_additional_sid(self):
        transactions = self.astra_transactions(assign_short_ids=True)
        for transaction in transactions:
            self.sut.msg_tx(transaction)

        # rebroadcast transactions with more sids
        for i, transaction in enumerate(transactions):
            transaction._short_id += 20
            self.sut.msg_tx(transaction)

        for i, transaction in enumerate(transactions):
            transaction_hash = transaction.tx_hash()
            self.assertTrue(self.gateway_node.get_tx_service().has_transaction_contents(transaction_hash))
            self.assertTrue(self.gateway_node.get_tx_service().has_transaction_short_id(transaction_hash))

            stored_hash, stored_content, _ = self.gateway_node.get_tx_service().get_transaction(i + 1)
            self.assertEqual(transaction_hash, stored_hash)
            self.assertEqual(transaction.tx_val(), stored_content)

            stored_hash2, stored_content2, _ = self.gateway_node.get_tx_service().get_transaction(i + 21)
            self.assertEqual(transaction_hash, stored_hash2)
            self.assertEqual(transaction.tx_val(), stored_content2)

        # only 10 times even with rebroadcast SID
        self.assertEqual(len(transactions), self.gateway_node.broadcast.call_count)

    def test_msg_tx_duplicate_ignore(self):
        transactions = self.astra_transactions(assign_short_ids=True)
        for transaction in transactions:
            self.sut.msg_tx(transaction)

        for transaction in transactions:
            self.sut.msg_tx(transaction)

        self.assertEqual(len(transactions), self.gateway_node.broadcast.call_count)

    @skip("Encrpytion in Ontology is not developed yet")
    def test_get_txs_block_recovery_encrypted(self):
        block: BlockOntMessage = self.ont_block()
        transactions: List[TxOntMessage] = self.ont_transactions(block)

        # assign short ids that the local connection won't know about until it gets the txs message
        remote_transaction_service = ExtensionTransactionService(MockNode(
            gateway_helpers.get_gateway_opts(8999)), 0)
        short_id_mapping = {}
        for i, transaction in enumerate(transactions):
            tx_hash = transaction.tx_hash()
            transaction_key = remote_transaction_service.get_transaction_key(tx_hash)

            remote_transaction_service.assign_short_id_by_key(transaction_key, i + 1)
            remote_transaction_service.set_transaction_contents_by_key(transaction_key, transaction.rawbytes())
            short_id_mapping[tx_hash] = TransactionInfo(tx_hash, transaction.rawbytes(), i + 1)

        astra_block = bytes(
            self.gateway_node.message_converter.block_to_astra_block(
                block, remote_transaction_service, True, self.gateway_node.network.min_tx_age_seconds
            )[0]
        )

        self.gateway_node.block_recovery_service.add_block = \
            MagicMock(wraps=self.gateway_node.block_recovery_service.add_block)
        self.gateway_node.broadcast = MagicMock()

        key, ciphertext = symmetric_encrypt(astra_block)
        block_hash = crypto.double_sha256(ciphertext)
        key_message = KeyMessage(Sha256Hash(block_hash), DEFAULT_NETWORK_NUM, "", key)
        broadcast_message = BroadcastMessage(Sha256Hash(block_hash), DEFAULT_NETWORK_NUM, "",
                                             BroadcastMessageType.BLOCK, True, ciphertext)

        self.sut.msg_broadcast(broadcast_message)

        self.gateway_node.broadcast.reset_mock()
        self.sut.msg_key(key_message)

        self.gateway_node.block_recovery_service.add_block.assert_called_once()
        self.assertEqual(2, self.gateway_node.broadcast.call_count)

        recovery_broadcast = self.gateway_node.broadcast.call_args_list[0]
        ((gettxs_message,), recovery_kwargs) = recovery_broadcast
        self.assertIsInstance(gettxs_message, GetTxsMessage)
        self.assertIn(ConnectionType.RELAY_TRANSACTION, recovery_kwargs["connection_types"])

        key_broadcast = self.gateway_node.broadcast.call_args_list[1]
        ((key_message, _conn), recovery_kwargs) = key_broadcast
        self.assertIsInstance(key_message, KeyMessage)
        self.assertIn(ConnectionType.GATEWAY, recovery_kwargs["connection_types"])

        txs = [tx for tx in short_id_mapping.values()]
        txs_message = TxsMessage(txs=txs)
        self.sut.msg_txs(txs_message)

        self._assert_block_sent(block)

    def test_get_txs_block_recovery(self):
        block: BlockOntMessage = self.ont_block()
        transactions: List[TxOntMessage] = self.ont_transactions(block)

        # assign short ids that the local connection won't know about until it gets the txs message
        remote_transaction_service = ExtensionTransactionService(MockNode(
            gateway_helpers.get_gateway_opts(8999)), 0)
        short_id_mapping = {}
        for i, transaction in enumerate(transactions):
            tx_hash = transaction.tx_hash()

            remote_transaction_service.assign_short_id(tx_hash, i + 1)
            remote_transaction_service.set_transaction_contents(tx_hash, transaction.rawbytes())
            short_id_mapping[tx_hash] = TransactionInfo(tx_hash, transaction.rawbytes(), i + 1)

        astra_block = bytes(
            self.gateway_node.message_converter.block_to_astra_block(
                block, remote_transaction_service, True, self.gateway_node.network.min_tx_age_seconds
            )[0]
        )

        self.gateway_node.block_recovery_service.add_block = \
            MagicMock(wraps=self.gateway_node.block_recovery_service.add_block)
        self.gateway_node.broadcast = MagicMock()

        broadcast_message = BroadcastMessage(block.block_hash(), DEFAULT_NETWORK_NUM, "",
                                             BroadcastMessageType.BLOCK, False, bytearray(astra_block))

        self.sut.msg_broadcast(broadcast_message)

        self.gateway_node.block_recovery_service.add_block.assert_called_once()
        self.assertEqual(1, self.gateway_node.broadcast.call_count)

        recovery_broadcast = self.gateway_node.broadcast.call_args_list[0]
        ((gettxs_message,), recovery_kwargs) = recovery_broadcast
        self.assertIsInstance(gettxs_message, GetTxsMessage)
        self.assertIn(ConnectionType.RELAY_TRANSACTION, recovery_kwargs["connection_types"])

        txs = [tx for tx in short_id_mapping.values()]
        txs_message = TxsMessage(txs=txs)
        self.sut.msg_txs(txs_message)

        self._assert_block_sent(block)

    def test_get_txs_multiple_sid_assignments(self):
        block = self.ont_block()
        transactions = self.ont_transactions(block)

        # assign short ids that the local connection won't know about until it gets the txs message
        remote_transaction_service1 = ExtensionTransactionService(MockNode(
            gateway_helpers.get_gateway_opts(8999)), 0)
        short_id_mapping1 = {}
        for i, transaction in enumerate(transactions):
            remote_transaction_service1.assign_short_id(transaction.tx_hash(), i + 1)
            remote_transaction_service1.set_transaction_contents(transaction.tx_hash(), transaction.tx())
            short_id_mapping1[transaction.tx_hash()] = TransactionInfo(transaction.tx_hash(), transaction.tx(), i + 1)

        txs_message_1 = TxsMessage([tx for tx in short_id_mapping1.values()])
        self.sut.msg_txs(txs_message_1)

        for transaction_hash, tx_info in short_id_mapping1.items():
            transaction_key = self.gateway_node.get_tx_service().get_transaction_key(transaction_hash)
            self.assertEqual(tx_info.short_id, self.gateway_node.get_tx_service().get_short_id_by_key(transaction_key))
            stored_hash, stored_content, _ = self.gateway_node.get_tx_service().get_transaction(tx_info.short_id)
            self.assertEqual(transaction_hash, stored_hash)
            self.assertEqual(tx_info.contents, stored_content)

        remote_transaction_service2 = ExtensionTransactionService(MockNode(
            gateway_helpers.get_gateway_opts(8999)), 0)
        short_id_mapping2 = {}
        for i, transaction in enumerate(transactions):
            remote_transaction_service2.assign_short_id(transaction.tx_hash(), i + 101)
            remote_transaction_service2.set_transaction_contents(transaction.tx_hash(), transaction.tx())
            short_id_mapping2[transaction.tx_hash()] = TransactionInfo(transaction.tx_hash(), transaction.tx(), i + 101)

        txs_message_2 = TxsMessage([tx for tx in short_id_mapping2.values()])
        self.sut.msg_txs(txs_message_2)

        for transaction_hash, tx_info in short_id_mapping2.items():
            stored_hash, stored_content, _ = self.gateway_node.get_tx_service().get_transaction(tx_info.short_id)
            self.assertEqual(transaction_hash, stored_hash)
            self.assertEqual(tx_info.contents, stored_content)

    def _assert_block_sent(self, ont_block):
        for node_conn in self.blockchain_connections:
            node_conn.enqueue_msg.assert_called()
            calls = node_conn.enqueue_msg.call_args_list

            sent_to_blockchain_calls = []
            for call in calls:
                sent_to_blockchain_calls.append(call)
            self.assertEqual(1, len(sent_to_blockchain_calls))

            ((sent_inv_msg,), _) = sent_to_blockchain_calls[0]
            self.assertIsInstance(sent_inv_msg, InvOntMessage)
            sent_inv_msg = cast(InvOntMessage, sent_inv_msg)

            sent_inv_type, sent_inv_hash = sent_inv_msg.inv_type()
            self.assertEqual(InventoryOntType.MSG_BLOCK.value, sent_inv_type)
            self.assertEqual(ont_block.block_hash(), sent_inv_hash[0])

    def _get_sample_block(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(root_dir, "samples/ont_sample_block.txt")) as sample_file:
            ont_block = sample_file.read().strip("\n")
        buf = bytearray(convert.hex_to_bytes(ont_block))
        parsed_block = BlockOntMessage(buf=buf)
        self.magic = parsed_block.magic()
        self.version = parsed_block.version()
        return parsed_block
