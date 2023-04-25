from ....models.locale.enums.time_periods import TimePeriods
from ....models.locale.enums.querytype import QueryType
from ..querytypes.querytypes import QUERYTYPES
from dataclasses import dataclass
from ..locale_model import Locale_Type


@dataclass
class VregBelgium(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.Max
        self.charged_peak = QueryType.Max
        self.query_model = QUERYTYPES[QueryType.Max]
        # TODO: to be decided. Should charged_peak be turned into the real charged peak, ie the average of the months in a year? could be issues with the long term stats there and it won't help peaq in any way.
        self.peak_cycle = TimePeriods.QuarterHourly


# https://www.vreg.be/nl/nieuwe-nettarieven
