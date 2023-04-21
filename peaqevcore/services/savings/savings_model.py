from dataclasses import dataclass, field
from .savings_status import SavingsStatus
from datetime import date, datetime
from typing import Tuple
import logging

_LOGGER = logging.getLogger(__name__)


@dataclass
class SavingsModel:
    peak_price_per_kwh: float
    car_connected_at: datetime | None = None
    prices: dict[date, list[float]] = field(default_factory=lambda: {})
    consumption: dict[date, dict[int, float]] = field(default_factory=lambda: {})
    # peaks: dict[date, dict[int, float]] = field(default_factory=lambda: {})
    status: SavingsStatus = SavingsStatus.Off

    async def async_reset(self) -> None:
        self.status = SavingsStatus.Off
        self.prices = {}
        self.consumption = {}
        # self.peaks = {}

    async def async_re_initialize(self, incoming: dict):
        self.car_connected_at = incoming.get("car_connected_at", None)
        self.prices = incoming.get("prices", {})
        self.consumption = incoming.get("consumption", {})
        # self.peaks = incoming.get("peaks", {})
        if all(
            [
                self.car_connected_at is not None,
                len(self.prices) > 0,
                len(self.consumption) > 0,
                # len(self.peaks) > 0,
            ]
        ):
            self.status = SavingsStatus.Collecting
        else:
            _LOGGER.warning("Cannot re-initialize SavingsModel, missing data")

    async def async_add_prices(
        self, prices: list[float], _date: date | None = None
    ) -> None:
        if _date is None:
            _date = datetime.now().date()
        self.prices[_date] = prices

    async def async_add_to_consumption(
        self,
        consumption: float,
        date: date | None = None,
        hour: int | None = None,
    ) -> None:
        if self.status is not SavingsStatus.Collecting:
            return
        _date, _hour = await self.async_check_date_hour(date, hour)
        await self.async_try_add(_date, _hour, self.consumption)
        self.consumption[_date][_hour] = max(
            [consumption, self.consumption[_date][_hour]]
        )

    # async def async_add_to_peaks(
    #     self, peak: float, date: date | None = None, hour: int | None = None
    # ) -> None:
    #     if self.status is not SavingsStatus.Collecting:
    #         return
    #     _date, _hour = await self.async_check_date_hour(date, hour)
    #     await self.async_try_add(_date, _hour, self.peaks)
    #     self.peaks[_date][_hour] = max([peak, self.peaks[_date][_hour]])

    async def async_check_date_hour(
        self, _date: date | None, _hour: int | None
    ) -> Tuple[date, int]:
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
