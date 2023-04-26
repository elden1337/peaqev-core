from ....models.locale.enums.querytype import QueryType
from ..querytypes.querytypes import QUERYTYPES
from ..locale_model import Locale_Type
from dataclasses import dataclass


@dataclass
class NO_Tensio(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_LNett(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeHours
        self.charged_peak = QueryType.AverageOfThreeHours
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeHours]


# docs: https://www.l-nett.no/nynettleie/slik-blir-ny-nettleie-og-pris


@dataclass
class NO_GlitreEnergi(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.Max
        self.charged_peak = QueryType.Max
        self.query_model = QUERYTYPES[QueryType.Max]


# docs: https://www.glitreenergi-nett.no/smart-nettleie/


@dataclass
class NO_AgderEnergi(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_Elvia(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_Lede(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_BKK(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_Mellom(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


@dataclass
class NO_AskerNett(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]


# docs: https://askernett.no/ny-nettleiemodell-for-alle-fra-1-juli-2022/
