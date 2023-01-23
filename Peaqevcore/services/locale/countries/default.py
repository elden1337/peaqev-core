from ....models.locale.enums.querytype import QueryType
from ..time_pattern import TimePattern
from ....models.locale.enums.calendar_periods import CalendarPeriods
from ..locale_model import Locale_Type
from dataclasses import dataclass

@dataclass(frozen=True)
class Default(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max


@dataclass(frozen=True)
class NoPeak(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    free_charge_pattern = TimePattern([
        {
            CalendarPeriods.Month: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            CalendarPeriods.Weekday: [0, 1, 2, 3, 4, 5, 6],
            CalendarPeriods.Hour: [0, 1, 2, 3, 4, 5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
        }
    ])