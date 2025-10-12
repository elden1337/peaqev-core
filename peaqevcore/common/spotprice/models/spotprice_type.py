from enum import Enum

from peaqevcore.common.spotprice.const import NORDPOOL, ENERGIDATASERVICE, GESPOT


class SpotPriceType(Enum):
    NordPool = NORDPOOL
    EnergidataService = ENERGIDATASERVICE
    GESpot = GESPOT
    Auto = 'Auto'
