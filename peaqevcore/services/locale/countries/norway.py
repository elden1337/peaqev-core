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
        self.price = LocalePrice(
            price_type=PriceType.Tiered,
            currency="NOK",
            _values=[
                TieredPrice(
                    upper_peak_limit=2,
                    value=126,
              ),
              TieredPrice(
                    upper_peak_limit=5,
                    value=225,
              ),
              TieredPrice(
                    upper_peak_limit=10,
                    value=385,
              ),
              TieredPrice(
                    upper_peak_limit=15,
                    value=567,
              ),
              TieredPrice(
                    upper_peak_limit=20,
                    value=749,
              ),
              TieredPrice(
                    upper_peak_limit=25,
                    value=933,
              ),
              TieredPrice(
                    upper_peak_limit=50,
                    value=1603,
              ),
              TieredPrice(
                    upper_peak_limit=75,
                    value=2516,
              ),
              TieredPrice(
                    upper_peak_limit=100,
                    value=3429,
              )
            ])

        """
        0 - 2	 126
        2 - 5	225
        5 - 10	 385
        10 - 15	 567
        15 - 20	 749
        20 - 25	 933
        25 - 50	1 603
        50 - 75	2 516
        75 - 100
        3 429
        100 - 150	4 953
        150 - 200	6 778
        200 - 300 	9 822
        300 - 400 	13 479
        400 - 500 	17 130
        0ver 500 	20 785
        """


@dataclass
class NO_LNett(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]
        self.price = LocalePrice(
            price_type=PriceType.Tiered,
            currency="NOK",
            _values=[
                TieredPrice(
                    upper_peak_limit=5,
                    value=285,
              ),
              TieredPrice(
                    upper_peak_limit=10,
                    value=435,
              ),
              TieredPrice(
                    upper_peak_limit=15,
                    value=585,
              ),
              TieredPrice(
                    upper_peak_limit=20,
                    value=735,
              ),
              TieredPrice(
                    upper_peak_limit=25,
                    value=885,
              )
            ])

# docs: https://www.l-nett.no/nynettleie/slik-blir-ny-nettleie-og-pris


@dataclass
class NO_GlitreEnergi(Locale_Type):
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
                    value=155,
              ),
              TieredPrice(
                    upper_peak_limit=5,
                    value=195,
              ),
              TieredPrice(
                    upper_peak_limit=10,
                    value=335,
              ),
              TieredPrice(
                    upper_peak_limit=15,
                    value=690,
              ),
              TieredPrice(
                    upper_peak_limit=20,
                    value=900,
              )
            ])


# docs: https://www.glitreenergi-nett.no/smart-nettleie/


@dataclass
class NO_AgderEnergi(Locale_Type):
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
                    value=155,
              ),
              TieredPrice(
                    upper_peak_limit=5,
                    value=195,
              ),
              TieredPrice(
                    upper_peak_limit=10,
                    value=335,
              ),
              TieredPrice(
                    upper_peak_limit=15,
                    value=690,
              ),
              TieredPrice(
                    upper_peak_limit=20,
                    value=900,
              )
            ])

@dataclass
class NO_Elvia(Locale_Type):
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
                    value=120,
              ),
              TieredPrice(
                    upper_peak_limit=5,
                    value=190,
              ),
              TieredPrice(
                    upper_peak_limit=10,
                    value=305,
              ),
              TieredPrice(
                    upper_peak_limit=15,
                    value=420,
              ),
              TieredPrice(
                    upper_peak_limit=20,
                    value=535,
              )
            ])

"""
0-2     120
2-5     190
5-10    305
10-15   420
15-20   535
"""

@dataclass
class NO_Lede(Locale_Type):
    def __post_init__(self):
        self.observed_peak = QueryType.AverageOfThreeDays
        self.charged_peak = QueryType.AverageOfThreeDays
        self.query_model = QUERYTYPES[QueryType.AverageOfThreeDays]
        self.price = LocalePrice(
            price_type=PriceType.Tiered,
            currency="NOK",
            _values=[
              TieredPrice(
                    upper_peak_limit=5,
                    value=262.5,
              ),
              TieredPrice(
                    upper_peak_limit=10,
                    value=448.75,
              ),
              TieredPrice(
                    upper_peak_limit=15,
                    value=632.5,
              ),
              TieredPrice(
                    upper_peak_limit=20,
                    value=818.75,
              ),
              TieredPrice(
                    upper_peak_limit=25,
                    value=1003.75,
              ),
              TieredPrice(
                    upper_peak_limit=50,
                    value=1560,
              ),
              TieredPrice(
                    upper_peak_limit=75,
                    value=2486.25,
              ),
              TieredPrice(
                    upper_peak_limit=100,
                    value=3412.5,
              ),
            ])

@dataclass
class NO_BKK(Locale_Type):
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
                    value=145,
              ),
              TieredPrice(
                    upper_peak_limit=5,
                    value=240,
              ),
              TieredPrice(
                    upper_peak_limit=10,
                    value=400,
              ),
              TieredPrice(
                    upper_peak_limit=15,
                    value=570,
              ),
              TieredPrice(
                    upper_peak_limit=20,
                    value=735,
              ),
              TieredPrice(
                    upper_peak_limit=25,
                    value=900,
              )
            ])

@dataclass
class NO_Mellom(Locale_Type):
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
                    value=243,
              ),
              TieredPrice(
                    upper_peak_limit=5,
                    value=364,
              ),
              TieredPrice(
                    upper_peak_limit=10,
                    value=607,
              ),
              TieredPrice(
                    upper_peak_limit=15,
                    value=801,
              ),
              TieredPrice(
                    upper_peak_limit=20,
                    value=1008,
              ),
              TieredPrice(
                    upper_peak_limit=25,
                    value=1263,
              ),
              TieredPrice(
                    upper_peak_limit=50,
                    value=1590,
              ),
              TieredPrice(
                    upper_peak_limit=999,
                    value=2125,
              )
            ])


@dataclass
class NO_AskerNett(Locale_Type):
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
                    value=185,
                ),
                TieredPrice(
                    upper_peak_limit=5,
                    value=230,
                ),
                TieredPrice(
                    upper_peak_limit=10,
                    value=340,
                ),
                TieredPrice(
                    upper_peak_limit=15,
                    value=710,
                ),
                TieredPrice(
                    upper_peak_limit=20,
                    value=895,
                ),
                TieredPrice(
                    upper_peak_limit=25,
                    value=1130,
                ),
                TieredPrice(
                    upper_peak_limit=50,
                    value=1600,
                ),
                TieredPrice(
                    upper_peak_limit=75,
                    value=2540,
                ),
                TieredPrice(
                    upper_peak_limit=100,
                    value=3380,
                ),
                TieredPrice(
                    upper_peak_limit=999,
                    value=5400,
                ),
            ])
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
            ])
        
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



