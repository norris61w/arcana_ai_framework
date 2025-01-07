import astragateway.messages.btc.btc_message_converter_factory as converter_factory
from astracommon.network.abstract_socket_connection_protocol import AbstractSocketConnectionProtocol
from astragateway.connections.abstract_gateway_blockchain_connection import AbstractGatewayBlockchainConnection
from astragateway.connections.abstract_gateway_node import AbstractGatewayNode
from astragateway.connections.abstract_relay_connection import AbstractRelayConnection
from astragateway.connections.btc.btc_node_connection import BtcNodeConnection
from astragateway.connections.btc.btc_relay_connection import BtcRelayConnection
from astragateway.connections.btc.btc_remote_connection import BtcRemoteConnection
from astragateway.services.abstract_block_cleanup_service import AbstractBlockCleanupService
from astragateway.services.btc.btc_block_processing_service import BtcBlockProcessingService
from astragateway.services.btc.btc_block_queuing_service import BtcBlockQueuingService
from astragateway.services.btc.btc_normal_block_cleanup_service import BtcNormalBlockCleanupService
from astragateway.services.push_block_queuing_service import PushBlockQueuingService
from astragateway.testing.btc_lossy_relay_connection import BtcLossyRelayConnection
from astragateway.testing.test_modes import TestModes
from astrautils.services.node_ssl_service import NodeSSLService


class BtcGatewayNode(AbstractGatewayNode):
    def __init__(self, opts, node_ssl_service: NodeSSLService):
        super(BtcGatewayNode, self).__init__(opts, node_ssl_service)

        self.block_processing_service = BtcBlockProcessingService(self)

        self.message_converter = converter_factory.create_btc_message_converter(
            self.opts.blockchain_net_magic,
            self.opts
        )

    def build_blockchain_connection(
        self, socket_connection: AbstractSocketConnectionProtocol
    ) -> AbstractGatewayBlockchainConnection:
        return BtcNodeConnection(socket_connection, self)

    def build_relay_connection(self, socket_connection: AbstractSocketConnectionProtocol) -> AbstractRelayConnection:
        if TestModes.DROPPING_TXS in self.opts.test_mode:
            cls = BtcLossyRelayConnection
        else:
            cls = BtcRelayConnection

        relay_connection = cls(socket_connection, self)
        return relay_connection

    def build_remote_blockchain_connection(
        self, socket_connection: AbstractSocketConnectionProtocol
    ) -> AbstractGatewayBlockchainConnection:
        return BtcRemoteConnection(socket_connection, self)

    def build_block_queuing_service(
        self,
        connection: AbstractGatewayBlockchainConnection
    ) -> PushBlockQueuingService:
        return BtcBlockQueuingService(self, connection)

    def build_block_cleanup_service(self) -> AbstractBlockCleanupService:
        if self.opts.use_extensions:
            from astragateway.services.btc.btc_extension_block_cleanup_service import BtcExtensionBlockCleanupService
            block_cleanup_service = BtcExtensionBlockCleanupService(self, self.network_num)
        else:
            block_cleanup_service = BtcNormalBlockCleanupService(self, self.network_num)
        return block_cleanup_service
