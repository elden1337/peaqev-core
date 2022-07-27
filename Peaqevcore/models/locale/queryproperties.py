from dataclasses import dataclass
from .enums import SumTypes, TimePeriods
from ...services.locale.querytypes.queryservice import QueryService

@dataclass(frozen=True)
class QueryProperties:
    sumtype: SumTypes
    timecalc:TimePeriods
    cycle: TimePeriods
    queryservice: QueryService