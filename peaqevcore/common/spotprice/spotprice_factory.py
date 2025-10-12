import logging

from peaqevcore.common.spotprice.const import *
from peaqevcore.common.spotprice.energidataservice import EnergiDataServiceUpdater
from peaqevcore.common.spotprice.gespot import GESpotUpdater
from peaqevcore.common.spotprice.models.spotprice_type import SpotPriceType
from peaqevcore.common.spotprice.nordpool import NordPoolUpdater
from peaqevcore.common.spotprice.spotpricebase import SpotPriceBase
from peaqevcore.common.models.peaq_system import PeaqSystem

_LOGGER = logging.getLogger(__name__)


class SpotPriceFactory:

    sources = {
        SpotPriceType.NordPool: NordPoolUpdater,
        SpotPriceType.EnergidataService: EnergiDataServiceUpdater,
        SpotPriceType.GESpot: GESpotUpdater
    }

    @staticmethod
    def create(
        hub, 
        observer, 
        system: PeaqSystem,
        test: bool = False, 
        is_active: bool = False,
        custom_sensor: str = None,
        spotprice_type: SpotPriceType = SpotPriceType.NordPool
    ) -> SpotPriceBase:
        if test:
            return NordPoolUpdater(hub, observer, system, test, is_active, custom_sensor)
        source = SpotPriceFactory.test_connections(hub.state_machine, spotprice_type, system, custom_sensor)
        return SpotPriceFactory.sources[source](hub, observer, system, test, is_active, custom_sensor)

    @staticmethod
    def test_connections(hass, spotprice_type: SpotPriceType, system: PeaqSystem, custom_sensor: str = None) -> SpotPriceType:
        """Test which price source is available and should be used.
        
        Priority order:
        1. Explicit spotprice_type if not Auto
        2. GE-Spot if entities found
        3. EnergiDataService if sensor exists
        4. Nordpool as fallback
        
        Args:
            hass: Home Assistant instance
            spotprice_type: Requested price source type
            system: PeaqSystem identifier
            custom_sensor: Optional custom sensor entity ID
            
        Returns:
            SpotPriceType to use
        """
        # If explicitly set to Nordpool from peaqev, honor it
        if spotprice_type == SpotPriceType.NordPool and system == PeaqSystem.PeaqEv:
            return SpotPriceType.NordPool
        
        # Check for GE-Spot (higher priority than other auto-detected sources)
        import homeassistant.helpers.template as template
        try:
            gespot_entities = template.integration_entities(hass, GESPOT)
            if len(list(gespot_entities)) > 0:
                _LOGGER.info("GE-Spot integration detected, using it for spot prices")
                return SpotPriceType.GESpot
        except Exception as e:
            _LOGGER.debug(f"GE-Spot not available: {e}")
        
        # Check for EnergiDataService
        sensor = hass.states.get(ENERGIDATASERVICE_SENSOR)       
        if sensor or (custom_sensor and custom_sensor == ENERGIDATASERVICE_SENSOR):
            return SpotPriceType.EnergidataService
        
        # Fallback to Nordpool
        return SpotPriceType.NordPool
