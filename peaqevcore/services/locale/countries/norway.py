from ....models.locale.enums.querytype import QueryType
from ..querytypes.querytypes import QUERYTYPES
from ..locale_model import Locale_Type
from ....models.locale.price.locale_price import LocalePrice
from ....models.locale.enums.price_type import PriceType
from ....models.locale.price.models.tiered_price import TieredPrice
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


@dataclass
class NO_Linja(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]
        self.price = LocalePrice(
            price_type=PriceType.Tiered,
            currency="NOK",
            _values=[
                TieredPrice(
                    upper_peak_limit=2,
                    value=263,
                ),
                TieredPrice(
                    upper_peak_limit=2,
                    value=263,
                ),
                TieredPrice(
                    upper_peak_limit=5,
                    value=329,
                ),
                TieredPrice(
                    upper_peak_limit=10,
                    value=395,
                ),
                TieredPrice(
                    upper_peak_limit=15,
                    value=658,
                ),
                TieredPrice(
                    upper_peak_limit=20,
                    value=789,
                ),
                TieredPrice(
                    upper_peak_limit=25,
                    value=920,
                ),
                TieredPrice(
                    upper_peak_limit=50,
                    value=1315,
                ),
                TieredPrice(
                    upper_peak_limit=75,
                    value=1446,
                ),
                TieredPrice(
                    upper_peak_limit=100,
                    value=1578,
                ),
                TieredPrice(
                    upper_peak_limit=999,
                    value=1973,
                ),
            ]
            
        """
        Trinn 1	0-2	263
        Trinn 2	2-5	329
        Trinn 3	5-10	395
        Trinn 4	10-15	658
        Trinn 5	15-20	789
        Trinn 6	20-25	920
        Trinn 7	25-50	1 315
        Trinn 8	50-75	1 446
        Trinn 9	75-100	1 578
        Trinn 10	Over 100	1 973
        """
    #docs: https://www.morenett.no/informasjon/nettleie-privat



