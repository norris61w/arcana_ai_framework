from typing import Union, Tuple, List

from mock import MagicMock

from astracommon.utils.object_hash import Sha256Hash
from astragateway.connections.abstract_gateway_node import AbstractGatewayNode
from astragateway.connections.eth.eth_gateway_node import EthGatewayNode
from astragateway.messages.eth.protocol.transactions_eth_protocol_message import TransactionsEthProtocolMessage
from astragateway.messages.ont.tx_ont_message import TxOntMessage
from astragateway.services.gateway_transaction_service import GatewayTransactionService
from astragateway.testing.abstract_gateway_transaction_service_test import TestAbstractGatewayTransactionService
from astragateway.testing.mocks import mock_eth_messages


class TestAbstractEthGatewayTransactionService(TestAbstractGatewayTransactionService):

    def _get_transaction_service(self) -> GatewayTransactionService:
        return GatewayTransactionService(self.node, 0)

    def _get_gateway_node(self) -> AbstractGatewayNode:
        mock_ssl_service = MagicMock()
        return EthGatewayNode(self.opts, mock_ssl_service)

    def _get_node_tx_message(
        self
    ) -> Tuple[
        Union[TxOntMessage, TransactionsEthProtocolMessage], List[Tuple[Sha256Hash, Union[bytearray, memoryview]]]
    ]:
        txs = [
            mock_eth_messages.get_dummy_transaction(1),
            mock_eth_messages.get_dummy_access_list_transaction(2)
        ]

        msg = TransactionsEthProtocolMessage(None, txs)

        # pyre-fixme [7]: Expected `Tuple[Union[TransactionsEthProtocolMessage, TxOntMessage], List[Tuple[Sha256Hash, Union[bytearray, memoryview]]]]`
        return msg, list(map(lambda tx: (tx.hash(), tx.contents()), msg.get_transactions()))
