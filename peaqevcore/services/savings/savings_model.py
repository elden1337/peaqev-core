
from dataclasses import dataclass, field
from .savings_status import SavingsStatus
from datetime import date, datetime
from typing import Tuple


@dataclass
class SavingsModel:
    peak_price_per_kwh: float
    prices: dict[date, list[float]] = field(default_factory=lambda: {})
    registered_consumption: dict[date, dict[int, float]] = field(default_factory=lambda: {})
    peaks: dict[date, dict[int, float]] = field(default_factory=lambda: {})
    status: SavingsStatus = SavingsStatus.Off

    async def async_add_prices(self, prices:list[float], _date: date = date.today()) -> None:
        self.prices[_date] = prices

    async def async_add_to_registered_consumption(self, registered_consumption:float, _date: date|None = None, _hour:int|None = None) -> None:
        _date, _hour = await self.async_check_date_hour(_date, _hour)
        await self.async_try_add(_date, _hour, self.registered_consumption)        
        self.registered_consumption[_date][_hour] +=registered_consumption

    async def async_add_to_peaks(self, peak:float, _date: date|None = None, _hour:int|None = None) -> None:
        _date, _hour = await self.async_check_date_hour(_date, _hour)
        await self.async_try_add(_date, _hour, self.peaks)
        self.peaks[_date][_hour] += peak

    async def async_check_date_hour(self, _date: date|None, _hour:int|None) -> Tuple[date, int]:
        if _date is None:
            _date = date.today()
        if _hour is None:
            _hour = datetime.now().hour
        return _date, _hour

    async def async_try_add(self, _date, _hour, modeldict: dict):
        if _date not in modeldict:
            modeldict[_date] = {}
        if _hour not in modeldict[_date].keys():
            modeldict[_date][_hour] = 0