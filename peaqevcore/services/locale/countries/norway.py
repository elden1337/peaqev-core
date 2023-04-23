from ..querytypes.const import (
    QUERYTYPE_AVERAGEOFTHREEDAYS,
    QUERYTYPE_AVERAGEOFTHREEDAYS_MIN,
    QUERYTYPE_AVERAGEOFTHREEHOURS_MIN,
    QUERYTYPE_AVERAGEOFTHREEHOURS,
    QUERYTYPE_BASICMAX,
)
from ....models.locale.enums.querytype import QueryType
from ..querytypes.querytypes import QUERYTYPES
from ..locale_model import Locale_Type
from dataclasses import dataclass


@dataclass
class NO_Tensio(Locale_Type):
    observed_peak = QueryType.AverageOfThreeDays
    charged_peak = QueryType.AverageOfThreeDays
    query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_LNett(Locale_Type):
    observed_peak = QueryType.AverageOfThreeHours
    charged_peak = QueryType.AverageOfThreeHours
    query_model = QUERYTYPES[QueryType.AverageOfThreeHours]


# docs: https://www.l-nett.no/nynettleie/slik-blir-ny-nettleie-og-pris


@dataclass
class NO_GlitreEnergi(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]


# docs: https://www.glitreenergi-nett.no/smart-nettleie/


@dataclass
class NO_AgderEnergi(Locale_Type):
    observed_peak = QueryType.AverageOfThreeDays
    charged_peak = QueryType.AverageOfThreeDays
    query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_Elvia(Locale_Type):
    observed_peak = QueryType.AverageOfThreeDays
    charged_peak = QueryType.AverageOfThreeDays
    query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_Lede(Locale_Type):
    observed_peak = QueryType.AverageOfThreeDays
    charged_peak = QueryType.AverageOfThreeDays
    query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_BKK(Locale_Type):
    observed_peak = QueryType.AverageOfThreeDays
    charged_peak = QueryType.AverageOfThreeDays
    query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_Mellom(Locale_Type):
    observed_peak = QueryType.AverageOfThreeDays
    charged_peak = QueryType.AverageOfThreeDays
    query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_AskerNett(Locale_Type):
    observed_peak = QueryType.AverageOfThreeDays
    charged_peak = QueryType.AverageOfThreeDays
    query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


# docs: https://askernett.no/ny-nettleiemodell-for-alle-fra-1-juli-2022/
