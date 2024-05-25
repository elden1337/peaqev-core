import logging
from typing import Tuple
from .hoursbase import Hours
from ..hoursselection import Hoursselection as core_hours
from ...hoursselection_service_new.models.hour_price import HourPrice
from ....common.enums.cautionhourtype import CautionHourType
from ...timer.timer import Timer
from ...scheduler.scheduler_facade import SchedulerFacade

_LOGGER = logging.getLogger(__name__)


class PriceAwareHours(Hours):
    def __init__(self, hub):
        self._hub = hub
        self.timer = Timer()
        self._cautionhour_type_string = hub.options.price.cautionhour_type
        self._core = core_hours(
            absolute_top_price=self._set_absolute_top_price(
                hub.options.price.top_price
            ),
            min_price=hub.options.price.min_price,
            cautionhour_type=self._cautionhour_type_string,
            non_hours=hub.options.nonhours
        )
        self._hass = hub.state_machine
        self._prices = []
        self.scheduler = SchedulerFacade(options=self.options)
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
    def future_hours(self) -> list[HourPrice]:
        return self.scheduler.combine_future_hours(self._core.future_hours)

    @property
    def absolute_top_price(self):
        return self._core.model.options.absolute_top_price

    @property
    def min_price(self):
        return self._core.model.options.min_price

    @property
    def prices(self) -> list:
        return self._core.prices

    @property
    def prices_tomorrow(self) -> list:
        return self._core.prices_tomorrow

    @property
    def adjusted_average(self) -> float|None:
        return self._core.adjusted_average

    @adjusted_average.setter
    def adjusted_average(self, val):
        if isinstance(val, (float, int)):
            self._core.adjusted_average = val

    @property
    def stopped_string(self) -> str:
        return self._core.service.allowance.display_name

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

    async def async_update_prices(
        self, prices: list = [], prices_tomorrow: list = []
    ) -> None:
        await self._core.async_update_prices(prices, prices_tomorrow)

    async def async_update_adjusted_average(self, val):
        await self._core.async_update_adjusted_average(val)

    async def async_get_average_kwh_price(self) -> Tuple[float | None, float | None]:
        if self._is_initialized:
            try:
                return await self._core.async_get_average_kwh_price()
            except ZeroDivisionError as e:
                _LOGGER.warning(f"get_average_kwh_price could not be calculated: {e}")
            return 0, None
        _LOGGER.debug("get avg kwh price, not initialized")
        return 0, None

    async def async_get_total_charge(self) -> Tuple[float, float | None]:
        if self._is_initialized:
            try:
                return await self._core.async_get_total_charge(
                    self._hub.sensors.current_peak.observed_peak
                )
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

    async def async_update_max_min(
        self,
        max_charge: float,
        session_energy: float | None = None,
        car_connected: bool = False,
        limiter: float = 0.0
    ):
        if not self._core.service.max_min.active:
            await self._core.service.max_min.async_setup(max_charge)
        await self._core.service.max_min.async_update(
            avg24=self._hub.sensors.powersensormovingaverage24.value,
            peak=self._hub.sensors.current_peak.observed_peak,
            max_desired=max_charge,
            session_energy=session_energy,
            car_connected=car_connected,
            limiter=limiter
        )
