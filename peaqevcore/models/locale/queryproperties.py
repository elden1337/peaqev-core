from dataclasses import dataclass, field
from .enums.sum_types import SumTypes
from .enums.time_periods import TimePeriods
from ...services.locale.querytypes.queryservice import QueryService


@dataclass(frozen=False)
class QueryProperties:
    sumtype: SumTypes
    timecalc: TimePeriods
    cycle: TimePeriods
    queryservice: QueryService = field(default_factory=lambda: QueryService())
