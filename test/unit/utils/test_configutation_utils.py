import unittest

from astragateway.utils import configuration_utils
from astragateway.models.config.gateway_node_config_model import GatewayNodeConfigModel
from astragateway import gateway_constants
from astracommon.test_utils.mocks.mock_node import MockNode
from astracommon.test_utils import helpers


class ConfigToolsTests(unittest.TestCase):
    """
    Unit tests for configuration utilities in the astragateway package.
    """

    def setUp(self):
        """
        Set up a mock node for testing purposes.
        """
        self.node = MockNode(helpers.get_common_opts(8888))

    def test_update_node_config_update_value(self):
        """
        Test that the node configuration is updated correctly when the new value is valid.
        """
        old_value = self.node.opts.throughput_stats_interval
        new_value = 90

        # Ensure the old and new values are different
        self.assertNotEqual(old_value, new_value)

        # Update the configuration value
        configuration_utils.compare_and_update(
            new_value,
            self.node.opts.throughput_stats_interval,
            item="throughput_stats_interval",
            setter=lambda val: self.node.opts.__setattr__("throughput_stats_interval", val)
        )

        # Check that the value has been updated
        self.assertEqual(self.node.opts.throughput_stats_interval, new_value)

    def test_update_node_config_ignore_missing_new_value(self):
        """
        Test that the node configuration is not updated when the new value is None.
        """
        old_value = self.node.opts.throughput_stats_interval
        new_value = None

        # Ensure the old value is not None
        self.assertIsNotNone(old_value)

        # Attempt to update with a None value
        configuration_utils.compare_and_update(
            new_value,
            self.node.opts.throughput_stats_interval,
            item="throughput_stats_interval",
            setter=lambda val: self.node.opts.__setattr__("throughput_stats_interval", val)
        )

        # Check that the value remains unchanged
        self.assertEqual(self.node.opts.throughput_stats_interval, old_value)

    def test_read_file(self):
        """
        Test reading configuration files and ensuring the correct model is returned.
        """
        # Test with an existing configuration file
        node_config_model = configuration_utils.read_config_file(gateway_constants.CONFIG_FILE_NAME)
        self.assertIsInstance(node_config_model, GatewayNodeConfigModel)

        # Test with a non-existent configuration file
        node_config_model = configuration_utils.read_config_file("NotAFileName.json")
        self.assertIsInstance(node_config_model, GatewayNodeConfigModel)
