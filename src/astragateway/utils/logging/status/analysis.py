from dataclasses import dataclass
from typing import List

from astragateway.utils.logging.status.environment import Environment
from astragateway.utils.logging.status.extension_modules_state import ExtensionModulesState
from astragateway.utils.logging.status.network import Network


@dataclass
class Analysis:
    time_started: str
    startup_parameters: str
    gateway_version: str
    extensions_check: ExtensionModulesState
    environment: Environment
    network: Network
    installed_python_packages: List[str]
