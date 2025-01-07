from dataclasses import dataclass
from astragateway.utils.logging.status.analysis import Analysis
from astragateway.utils.logging.status.summary import Summary


@dataclass
class Diagnostics:
    summary: Summary
    analysis: Analysis
