from dataclasses import dataclass
from .enums.time_periods import TimePeriods

@dataclass(frozen=True)
class SumCounter:
    counter:int = 1
    groupby: TimePeriods = TimePeriods.UnSet