from astragateway.services.extension_gateway_transaction_service import ExtensionGatewayTransactionService
from astragateway.services.gateway_transaction_service import GatewayTransactionService
from astragateway.testing.abstract_eth_gateway_transaction_service_test import TestAbstractEthGatewayTransactionService


class ExtensionEthGatewayTransactionServiceTest(TestAbstractEthGatewayTransactionService):

    def test_process_transactions_message_from_node(self):
        self._test_process_transactions_message_from_node()

    def _get_transaction_service(self) -> GatewayTransactionService:
        return ExtensionGatewayTransactionService(self.node, self.node.network_num)
