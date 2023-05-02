from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Tuple


@dataclass
class ConsumptionModel:
    consumption: dict[date, dict[int, float]] = field(default_factory=lambda: {})

    async def async_add_consumption(
        self,
        consumption: float,
        date: date | None = None,
        hour: int | None = None,
    ) -> None:
        _date, _hour = await self.async_check_date_hour(date, hour)
        await self.async_try_add(_date, _hour, self.consumption)
        self.consumption[_date][_hour] = max(
            [consumption, self.consumption[_date][_hour]]
        )

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
