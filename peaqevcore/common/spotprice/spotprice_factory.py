import logging

from peaqevcore.common.spotprice.const import *
from peaqevcore.common.spotprice.energidataservice import EnergiDataServiceUpdater
from peaqevcore.common.spotprice.nordpool import NordPoolUpdater
from peaqevcore.common.spotprice.spotpricebase import SpotPriceBase

_LOGGER = logging.getLogger(__name__)


class SpotPriceFactory:

    sources = {
        NORDPOOL: NordPoolUpdater,
        ENERGIDATASERVICE: EnergiDataServiceUpdater
    }

    @staticmethod
    def create(hub, observer, test:bool = False, is_active: bool = False) -> SpotPriceBase:
        if test:
            return NordPoolUpdater(hub, test, observer)
        source = SpotPriceFactory.test_connections(hub.state_machine)
        return SpotPriceFactory.sources[source](hub, observer, test, is_active)

    @staticmethod
    def test_connections(hass) -> str:
        sensor = hass.states.get(ENERGIDATASERVICE_SENSOR)       
        if sensor:
            _LOGGER.debug("Found sensor %s", sensor)
            return ENERGIDATASERVICE
        else:
            _LOGGER.debug("No sensor %s", sensor)
            return NORDPOOL
                

    