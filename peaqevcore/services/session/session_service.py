from __future__ import annotations
import time
from datetime import datetime, date
from .power_reading import PowerReading
from .energy_weekly import EnergyWeekly
from .session_model import SessionModel
from typing import Any
import logging

_LOGGER = logging.getLogger(__name__)


class SessionService:
    def __init__(self) -> None:
        self.model = SessionModel()
        self.average_data = EnergyWeekly()
        self._original_peak: float = 0
        self._current_date: date = date.today()
        self._current_hour: int = 0

    async def async_setup(
        self, init_average_data: dict | None = None, mock_time: float | None = None
    ) -> None:
        await self.average_data.async_setup(init_average_data)
        await self.async_set_delta(mock_time)

    @property
    def energy_average(self) -> float:
        return self.average_data.average

    @property
    def energy_weekly_dict(self) -> dict:
        return self.average_data.export

    @property
    def total_energy(self) -> float:
        return round(self.sync_get_status()["energy"]["value"], 3)

    @property
    def readings(self) -> list:
        return self.model.readings

    @property
    def total_price(self) -> float:
        return round(self.sync_get_status()["price"], 3)

    @total_price.setter
    def total_price(self, val):
        self.total_price = val

    @property
    def session_data(self) -> dict:
        return self.model.consumption

    @property
    def original_peak(self) -> float:
        return self._original_peak

    async def async_reset(self, original_peak: float = 0):
        self._original_peak = original_peak
        _init_avg = self.average_data.export
        self.__init__()
        await self.async_setup(_init_avg)

    async def async_terminate(self, mock_time: float | None = None):
        _now = mock_time or time.time()
        await self.async_update_power_reading(0, _now)
        _LOGGER.debug(
            f"Called terminate on session_price. Trying to add {self.total_energy} to statistics."
        )
        await self.average_data.async_update(self.total_energy, _now)
        await self.async_get_status()

    async def async_set_status(self) -> None:
        for i in self.model.readings:
            self.model.total_energy += i.reading_integral
            self.model.total_price += i.reading_cost
        await self.model.async_add_consumption(
            consumption=self.model.total_energy,
            date=self._current_date,
            hour=self._current_hour,
        )

    async def async_get_status(self) -> dict:
        self.model.total_energy = 0
        self.model.total_price = 0
        await self.async_set_status()
        return {
            "energy": {"value": self.model.total_energy, "unit": "kWh"},
            "price": self.model.total_price,
        }

    def sync_set_status(self) -> None:
        for i in self.model.readings:
            self.model.total_energy += i.reading_integral
            self.model.total_price += i.reading_cost

    def sync_get_status(self) -> dict:
        self.model.total_energy = 0
        self.model.total_price = 0
        self.sync_set_status()
        return {
            "energy": {"value": self.model.total_energy, "unit": "kWh"},
            "price": self.model.total_price,
        }

    async def async_update_power_reading(
        self, power: Any, mock_time: float | None = None
    ):
        await self.async_set_delta(mock_time or time.time())
        p = PowerReading(
            self.model.price, self.model.current_power, self.model.time_delta
        )
        self.model.readings.append(p)
        try:
            self.model.current_power = float(power)
        except:
            self.model.current_power = 0

    async def async_update_price(self, price: Any, mock_time: float | None = None):
        if self.model.current_power > 0:
            await self.async_update_power_reading(
                power=self.model.current_power, mock_time=mock_time or time.time()
            )
        try:
            self.model.price = float(price)
        except:
            self.model.price = 0

    async def async_set_delta(self, mock_time: float | None = None) -> None:
        now = mock_time or time.time()
        await self.async_update_date_and_hour(now)
        self.model.time_delta = now - self.model.current_time
        self.model.current_time = now

    async def async_update_date_and_hour(self, dt: float) -> None:
        date_time = datetime.fromtimestamp(dt)
        self._current_date = date_time.date()
        self._current_hour = date_time.hour
