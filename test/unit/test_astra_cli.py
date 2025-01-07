import sys
from argparse import ArgumentParser

from astracommon.test_utils.helpers import async_test
from astracommon.test_utils.abstract_test_case import AbstractTestCase
from astra_cli import main


class AstraCliTest(AbstractTestCase):
    """
    Unit tests for the Bloxroute CLI functionality.
    """

    @async_test
    async def test_cloud_api_good_invocation(self):
        """
        Test valid invocation for the cloud API.
        """
        argv = [
            "--account-id", "9333",
            "--secret-hash", "aaaa",
            "--cloud-api",
            "--blockchain-protocol", "Ethereum",
            "--blockchain-network", "mainnet",
            "command", "BLXR_TX"
        ]
        arg_parser = ArgumentParser()
        main.add_run_arguments(arg_parser)
        main.add_base_arguments(arg_parser)
        opts, params = arg_parser.parse_known_args(argv)

        stdout_writer = sys.stdout

        valid = main.validate_args(opts, stdout_writer)
        self.assertEqual(True, valid)

    @async_test
    async def test_cloud_api_wrong_invocation(self):
        """
        Test invalid invocation for the cloud API.
        """
        argv = [
            "--account-id", "9333",
            "--cloud-api",
            "--blockchain-protocol", "Ethereum",
            "--blockchain-network", "mainnet",
            "command", "BLXR_TX"
        ]
        arg_parser = ArgumentParser()
        main.add_run_arguments(arg_parser)
        main.add_base_arguments(arg_parser)
        opts, params = arg_parser.parse_known_args(argv)

        stdout_writer = sys.stdout

        valid = main.validate_args(opts, stdout_writer)
        self.assertEqual(False, valid)

    @async_test
    async def test_astra_cli_good_invocation(self):
        """
        Test valid invocation for the Astra CLI.
        """
        argv = [
            "--rpc-user", "",
            "--rpc-password", "",
            "--rpc-host", "17.2.17.0.1",
            "--rpc-port", "4444",
            "--blockchain-protocol", "Ethereum",
            "--blockchain-network", "mainnet",
            "command", "BLXR_TX"
        ]
        arg_parser = ArgumentParser()
        main.add_run_arguments(arg_parser)
        main.add_base_arguments(arg_parser)
        opts, params = arg_parser.parse_known_args(argv)

        stdout_writer = sys.stdout

        valid = main.validate_args(opts, stdout_writer)
        self.assertEqual(True, valid)

    @async_test
    async def test_astra_cli_wrong_invocation(self):
        """
        Test invalid invocation for the Astra CLI.
        """
        argv = [
            "--rpc-user", "",
            "--rpc-port", "4444",
            "--blockchain-protocol", "Ethereum",
            "--blockchain-network", "mainnet",
            "command", "BLXR_TX"
        ]
        arg_parser = ArgumentParser()
        main.add_run_arguments(arg_parser)
        main.add_base_arguments(arg_parser)
        opts, params = arg_parser.parse_known_args(argv)

        stdout_writer = sys.stdout

        valid = main.validate_args(opts, stdout_writer)
        self.assertEqual(False, valid)

    @async_test
    async def test_astra_cli_help_command(self):
        """
        Test help command invocation for the Astra CLI.
        """
        try:
            argv = ["help"]
            arg_parser = ArgumentParser()
            main.add_run_arguments(arg_parser)
            main.add_base_arguments(arg_parser)
            opts, params = arg_parser.parse_known_args(argv)

            stdout_writer = sys.stdout

            valid = main.validate_args(opts, stdout_writer)
            self.assertEqual(True, valid)
        except Exception as e:
            self.fail(f"Unexpected exception {e} raised")
