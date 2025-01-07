from dataclasses import dataclass

from astracommon.models.config.abstract_config_model import AbstractConfigModel
from astracommon.models.config.cron_config_model import CronConfigModel
from astracommon.models.config.log_config_model import LogConfigModel
from astracommon.models.config.stats_config_model import StatsConfigModel


@dataclass
class GatewayNodeConfigModel(AbstractConfigModel):
    # pyre-fixme[8]: Attribute has type `LogConfigModel`; used as `None`.
    log_config: LogConfigModel = None
    # pyre-fixme[8]: Attribute has type `StatsConfigModel`; used as `None`.
    stats_config: StatsConfigModel = None
    # pyre-fixme[8]: Attribute has type `CronConfigModel`; used as `None`.
    cron_config: CronConfigModel = None
