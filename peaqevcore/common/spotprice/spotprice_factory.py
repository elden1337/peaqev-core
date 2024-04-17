import logging

from peaqevcore.common.spotprice.const import *
from peaqevcore.common.spotprice.energidataservice import EnergiDataServiceUpdater
from peaqevcore.common.spotprice.nordpool import NordPoolUpdater
from peaqevcore.common.spotprice.spotpricebase import SpotPriceBase
from peaqevcore.common.models.peaq_system import PeaqSystem

_LOGGER = logging.getLogger(__name__)


from enum import Enum

class SpotPriceType(Enum):
    NordPool = NORDPOOL
    EnergidataService = ENERGIDATASERVICE


class SpotPriceFactory:

    sources = {
        SpotPriceType.NordPool: NordPoolUpdater,
        SpotPriceType.EnergidataService: EnergiDataServiceUpdater
    }

    @staticmethod
    def create(
        hub, 
        observer, 
        system: PeaqSystem,
        test:bool = False, 
        is_active: bool = False,
        custom_sensor: str = None
        ) -> SpotPriceBase:
        if test:
            return NordPoolUpdater(hub, test, system, observer)
        source = SpotPriceFactory.test_connections(hub.state_machine, custom_sensor)
        return SpotPriceFactory.sources[source](hub, observer, system, test, is_active, custom_sensor)

    @staticmethod
    def test_connections(hass, custom_sensor: str = None) -> SpotPriceType:
        sensor = hass.states.get(ENERGIDATASERVICE_SENSOR)       
        if sensor or (custom_sensor and custom_sensor == ENERGIDATASERVICE_SENSOR):
            return SpotPriceType.EnergidataService
        return SpotPriceType.NordPool
                

    