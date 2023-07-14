from dataclasses import dataclass, field
from datetime import datetime
from abc import abstractmethod
from ..const import NON_HOUR, CAUTION_HOUR, CHARGING_PERMITTED
from ...timer.timer import Timer
from ...scheduler.scheduler_facade import SchedulerFacade
from typing import Tuple


class Hours:
    timer: Timer
    scheduler: SchedulerFacade

    def __init__(
        self, price_aware: bool, non_hours: list = [], caution_hours: list = []
    ):
        self._non_hours = non_hours
        self._caution_hours = caution_hours
        self._price_aware = price_aware
        self._is_initialized = False

    @property
    def state(self) -> str:
        if datetime.now().hour in self.non_hours:
            return NON_HOUR
        if datetime.now().hour in self.caution_hours:
            return CAUTION_HOUR
        return CHARGING_PERMITTED

    @property
    def price_aware(self) -> bool:
        return self._price_aware

    @property
    @abstractmethod
    def non_hours(self):
        pass

    @property
    @abstractmethod
    def is_initialized(self):
        pass

    @non_hours.setter
    @abstractmethod
    def non_hours(self, val):
        pass

    @property
    @abstractmethod
    def caution_hours(self):
        pass

    @caution_hours.setter
    @abstractmethod
    def caution_hours(self, val):
        pass

    @property
    @abstractmethod
    def nordpool_entity(self):
        pass

    @abstractmethod
    def update_nordpool(self) -> None:
        pass

    @abstractmethod
    async def async_update_top_price(self, dyn_top_price) -> None:
        pass

    @property
    @abstractmethod
    def dynamic_caution_hours(self) -> dict:
        pass

    @property
    @abstractmethod
    def future_hours(self) -> list:
        pass

    @abstractmethod
    def update_prices(self, prices: list = [], prices_tomorrow: list = []) -> None:
        pass

    @property
    @abstractmethod
    def options(self):
        pass

    @property
    @abstractmethod
    def offsets(self) -> dict:
        pass

    @property
    def prices(self) -> list:
        return []

    @prices.setter
    @abstractmethod
    def prices(self, val):
        pass

    @property
    def prices_tomorrow(self) -> list:
        return []

    @prices_tomorrow.setter
    @abstractmethod
    def prices_tomorrow(self, val):
        pass

    @property
    @abstractmethod
    def absolute_top_price(self):
        pass

    @property
    @abstractmethod
    def min_price(self):
        pass

    @property
    @abstractmethod
    def cautionhour_type_string(self) -> str:
        pass

    @property
    @abstractmethod
    def adjusted_average(self) -> float:
        pass

    @adjusted_average.setter
    @abstractmethod
    def adjusted_average(self, val):
        pass

    @abstractmethod
    async def async_get_average_kwh_price(self) -> Tuple[float | None, float | None]:
        pass

    @abstractmethod
    async def async_get_total_charge(self) -> Tuple[float, float | None]:
        pass

    @abstractmethod
    async def async_update_adjusted_average(self, val):
        pass

    @abstractmethod
    async def async_update_max_min(
        self,
        max_charge: float,
        session_energy: float | None = None,
        car_connected: bool = False,
    ):
        pass
