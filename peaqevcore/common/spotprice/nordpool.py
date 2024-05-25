import asyncio
import logging

import homeassistant.helpers.template as template #todo: fix this

from peaqevcore.common.models.observer_types import ObserverTypes
from peaqevcore.common.spotprice.const import NORDPOOL
from peaqevcore.common.spotprice.models.spotprice_dto import NordpoolDTO
from peaqevcore.common.spotprice.spotpricebase import SpotPriceBase
from peaqevcore.common.models.peaq_system import PeaqSystem

_LOGGER = logging.getLogger(__name__)


class NordPoolUpdater(SpotPriceBase):
    def __init__(self, hub, observer, system: PeaqSystem, test:bool = False, is_active: bool = True, custom_sensor: str = None):
        super().__init__(
            hub=hub,
            source=NORDPOOL,
            system=system,
            test=test,
            is_active=is_active,
            observer=observer,
            custom_sensor=custom_sensor
        )

    async def async_set_dto(self, ret, initial: bool = False) -> None:
        _result = NordpoolDTO()
        await _result.set_model(ret)
        if await self.async_update_set_prices(_result):
            if initial:
                await self.hub.async_update_prices(
                    [self.model.prices, self.model.prices_tomorrow]
                )
                _LOGGER.info("Nordpool service has been successfully.")
                _LOGGER.debug("Nordpool service has been initialized. Broadcasting...")
                await self.hub.observer.async_broadcast(ObserverTypes.SpotpriceInitialized)
            else:
                await self.hub.observer.async_broadcast(ObserverTypes.PricesChanged,[self.model.prices, self.model.prices_tomorrow])
            self._is_initialized = True

    def setup(self):
        try:
            entities = template.integration_entities(self.state_machine, NORDPOOL)
            _LOGGER.debug(f"Found {list(entities)} Spotprice entities for {self.model.source}.")
            if len(list(entities)) < 1:
                if hasattr(self.hub.options, "price"):
                    self.hub.options.price.price_aware = False  # todo: composition
                _LOGGER.error(
                    f"There were no Spotprice-entities. Cannot continue. with price-awareness."
                )
            if len(list(entities)) == 1 or self.custom_sensor:
                if self.custom_sensor:
                    _LOGGER.info(f"Using custom sensor for spot-prices: {self.custom_sensor}")
                self._setup_set_entity(self.custom_sensor if self.custom_sensor else list(entities)[0])
            else:
                _found: bool = False
                for e in list(entities):
                    if self._test_sensor(e):
                        _found = True
                        self._setup_set_entity(e)
                        break
                if not _found:
                    self.hub.options.price.price_aware = False  # todo: composition todo: fix this
                    _LOGGER.error(f"more than one Spotprice entity found. Cannot continue with price-awareness.")
        except Exception as e:
            if hasattr(self.hub.options, "price"):
                self.hub.options.price.price_aware = False  # todo: composition
            _LOGGER.error(f"I was unable to get a Spotprice-entity. Cannot continue with price-awareness: {e}")

    def _setup_set_entity(self, entity: str) -> None:
        self.model.entity = entity
        _LOGGER.debug(
            f"Nordpool has been set up and is ready to be used with {self.entity}"
        )
        asyncio.run_coroutine_threadsafe(
            self.async_update_spotprice(initial=True),
            self.state_machine.loop,
        )

    def _test_sensor(self, sensor: str) -> bool:
        """
        Testing whether the sensor has a set value for additional_costs_current_hour.
        This is the only way we can differ when there are multiple sensors present.
        """
        _LOGGER.debug(f"testing sensor {sensor}")
        state = self.state_machine.states.get(sensor)
        if state:
            _LOGGER.debug(f"got state")
            attr = state.attributes.get("additional_costs_current_hour", 0)
            _LOGGER.debug(f"testing attribute {attr}")
            if attr != 0:
                return True
        return False
