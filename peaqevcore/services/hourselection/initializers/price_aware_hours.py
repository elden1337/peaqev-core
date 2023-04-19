import logging
from typing import Tuple
from .hoursbase import Hours
from ..hoursselection import Hoursselection as core_hours
from ....models.hourselection.cautionhourtype import CautionHourType
from ...timer.timer import Timer
from ...scheduler.scheduler_facade import SchedulerFacade

_LOGGER = logging.getLogger(__name__)

class PriceAwareHours(Hours):
    def __init__(
            self,
            hub
    ):
        self._hub = hub
        self.timer = Timer()
        self._cautionhour_type = CautionHourType.get_num_value(hub.options.price.cautionhour_type)
        self._cautionhour_type_string = hub.options.price.cautionhour_type
        self._core = core_hours(
            absolute_top_price=self._set_absolute_top_price(hub.options.price.top_price),
            min_price=hub.options.price.min_price,
            cautionhour_type=self._cautionhour_type_string, 
            blocknocturnal=hub.options.blocknocturnal
        )
        self._hass = hub.state_machine
        self._prices = []
        self.scheduler = SchedulerFacade(hub=self._hub, options=self.options)
        super().__init__(price_aware=True)

    @property
    def options(self):
        return self._core.model.options

    @property
    def dynamic_caution_hours(self) -> dict:
        if self.scheduler.scheduler_active:
            return self.scheduler.caution_hours
        return self._core.dynamic_caution_hours

    @property
    def cautionhour_type_string(self) -> str:
        return self._cautionhour_type_string

    @property
    def non_hours(self) -> list:
        if self.scheduler.scheduler_active:
            return self.scheduler.non_hours
        return self._core.non_hours

    @property
    def caution_hours(self) -> list:
        return self._core.caution_hours

    @property
    def absolute_top_price(self):
        return self._core.model.options.absolute_top_price

    @property
    def min_price(self):
        return self._core.model.options.min_price

    @property
    def prices(self) -> list:
        return self._core.prices

    @prices.setter
    def prices(self, val):
        self._core.prices = val

    @property
    def prices_tomorrow(self) -> list:
        return self._core.prices_tomorrow

    @prices_tomorrow.setter
    def prices_tomorrow(self, val):
        self._core.prices_tomorrow = val

    @property
    def adjusted_average(self) -> float:
        return self._core.adjusted_average

    @adjusted_average.setter
    def adjusted_average(self, val):
        if isinstance(val, (float, int)):
            self._core.adjusted_average = val

    @property
    def offsets(self) -> dict:
        return self._core.offsets

    @property
    def is_initialized(self) -> bool:
        if self.prices is not None:
            if len(self.prices):
                if self._is_initialized is False:
                    self._is_initialized = True
                    _LOGGER.debug("Hourselection has initialized")
                return True
        return False

    async def async_update_top_price(self, dyn_top_price) -> None: 
        if self._hub.options.price.dynamic_top_price:
            await self._core.async_update_top_price(dyn_top_price)

    async def async_update_prices(self, prices:list = [], prices_tomorrow:list=[]) -> None:
        await self._core.async_update_prices(prices, prices_tomorrow)

    async def async_update_adjusted_average(self, val):
        await self._core.async_update_adjusted_average(val)

    async def async_get_average_kwh_price(self) -> Tuple[float|None, float|None]:
        if self._is_initialized:
            try:
                return await self._core.async_get_average_kwh_price()
            except ZeroDivisionError as e:
                _LOGGER.warning(f"get_average_kwh_price could not be calculated: {e}")
            return 0, None
        _LOGGER.debug("get avg kwh price, not initialized")
        return 0 , None

    async def async_get_total_charge(self) -> Tuple[float, float|None]:
        if self._is_initialized:
            try:
                return await self._core.async_get_total_charge(self._hub.sensors.current_peak.value)
            except ZeroDivisionError as e:
                _LOGGER.warning(f"get_total_charge could not be calculated: {e}")
            return 0, None
        _LOGGER.debug("get avg kwh price, not initialized")
        return 0, None

    @staticmethod
    def _set_absolute_top_price(_input) -> float:
        if _input is None or _input <= 0:
            return float("inf")
        return _input
    
    async def async_update_max_min(self, max_charge):
        await self._core.max_min.async_setup(max_charge)
        await self._core.max_min.async_update(
            avg24=self._hub.sensors.powersensormovingaverage24.value, 
            peak=self._hub.sensors.current_peak.value, 
            max_desired=max_charge
            )