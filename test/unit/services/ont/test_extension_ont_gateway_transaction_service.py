from astragateway.services.extension_gateway_transaction_service import ExtensionGatewayTransactionService
from astragateway.services.gateway_transaction_service import GatewayTransactionService
from astragateway.testing.abstract_ont_gateway_transaction_service_test import TestAbstractOntGatewayTransactionService


class ExtensionOntGatewayTransactionServiceTest(TestAbstractOntGatewayTransactionService):

    def test_process_transactions_message_from_node(self):
        self._test_process_transactions_message_from_node()

    def _get_transaction_service(self) -> GatewayTransactionService:
        return ExtensionGatewayTransactionService(self.node, 33)
