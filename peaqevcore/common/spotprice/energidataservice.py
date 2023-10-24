import asyncio
import logging

from peaqevcore.common.models.observer_types import ObserverTypes
from peaqevcore.common.spotprice.const import (ENERGIDATASERVICE, ENERGIDATASERVICE_SENSOR)
from peaqevcore.common.spotprice.models.spotprice_dto import EnergiDataServiceDTO
from peaqevcore.common.spotprice.spotpricebase import SpotPriceBase
from peaqevcore.common.models.peaq_system import PeaqSystem

_LOGGER = logging.getLogger(__name__)


class EnergiDataServiceUpdater(SpotPriceBase):
    def __init__(self, hub, observer, system:PeaqSystem, test:bool = False, is_active: bool = True):
        super().__init__(hub=hub, source=ENERGIDATASERVICE, system=system, test=test, is_active=is_active, observer=observer)

    async def async_set_dto(self, ret, initial: bool = False) -> None:
        _result = EnergiDataServiceDTO()
        await _result.set_model(ret)
        if await self.async_update_set_prices(_result):
            if initial:
                await self.hub.async_update_prices(
                    [self.model.prices, self.model.prices_tomorrow]
                )
                await self.observer.async_broadcast(ObserverTypes.SpotpriceInitialized)
            else:
                await self.observer.async_broadcast(
                    ObserverTypes.PricesChanged,
                    [self.model.prices, self.model.prices_tomorrow],
                )
            self._is_initialized = True

    def setup(self):
        try:
            sensor = self.state_machine.states.get(ENERGIDATASERVICE_SENSOR)
            if not sensor.state:
                self.hub.options.price.price_aware = False  # todo: composition
                _LOGGER.error(
                    f"There were no Spotprice-entities. Cannot continue. with price-awareness."
                )
            else:
                self.model.entity = ENERGIDATASERVICE_SENSOR
                _LOGGER.debug(
                    f"EnergiDataService has been set up and is ready to be used with {self.model.entity}"
                )
                asyncio.run_coroutine_threadsafe(
                    self.async_update_spotprice(),
                    self.state_machine.loop,
                )
        except Exception as e:
            self.hub.options.price.price_aware = False  # todo: composition
            _LOGGER.error(
                f"I was unable to get a Spotprice-entity. Cannot continue. with price-awareness: {e}"
            )