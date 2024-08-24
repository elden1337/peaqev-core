from enum import Enum

from peaqevcore.common.spotprice.const import NORDPOOL, ENERGIDATASERVICE


class SpotPriceType(Enum):
    NordPool = NORDPOOL
    EnergidataService = ENERGIDATASERVICE
    Auto = 'Auto'