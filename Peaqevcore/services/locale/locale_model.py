from dataclasses import dataclass, field
from datetime import datetime

from ..locale.free_charge import FreeChargePattern
from .querytypes.const import (
HOURLY,
QUARTER_HOURLY
)
from .querytypes.querytypes import(
LocaleQuery
)


@dataclass(frozen=True)
class Locale_Type:
    observed_peak: str
    charged_peak: str
    query_model: LocaleQuery
    free_charge_pattern: FreeChargePattern = None
    peak_cycle: str = HOURLY
    #converted: bool = False #transition key to remove sql-dependency
    is_quarterly: bool = field(init=False, repr=False)

    def free_charge(self, mockdt: datetime=datetime.min) -> bool:
        if self.free_charge_pattern is None:
            return False
        now = datetime.now() if mockdt is datetime.min else mockdt
        return self.free_charge_pattern.free_charge(now)

    def is_quarterly(self) -> bool:
        return self.peak_cycle == QUARTER_HOURLY



