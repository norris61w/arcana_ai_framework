from astracommon.services.extension_transaction_service import ExtensionTransactionService, TransactionService
from astracommon.test_utils import helpers

from astragateway.services.ont.abstract_ont_block_cleanup_service import AbstractOntBlockCleanupService
from astragateway.services.ont.ont_extension_block_cleanup_service import OntExtensionBlockCleanupService
from astragateway.testing.abstract_ont_block_cleanup_service_test import AbstractOntBlockCleanupServiceTest


class OntExtensionBlockCleanupServiceTest(AbstractOntBlockCleanupServiceTest):

    def setUp(self) -> None:
        helpers.set_extensions_parallelism()
        super(OntExtensionBlockCleanupServiceTest, self).setUp()

    def test_mark_blocks_and_request_cleanup(self):
        self._test_mark_blocks_and_request_cleanup()

    def test_block_confirmation_cleanup(self):
        self._test_block_confirmation_cleanup()

    def test_block_cleanup(self):
        self._test_block_cleanup()

    def _get_transaction_service(self) -> TransactionService:
        return ExtensionTransactionService(self.node, 1)

    def _get_cleanup_service(self) -> AbstractOntBlockCleanupService:
        return OntExtensionBlockCleanupService(self.node, 1)

    def _get_file_path(self) -> str:
        return __file__
