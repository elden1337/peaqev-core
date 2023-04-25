from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...services.locale.querytypes.queryservice import QueryService
from dataclasses import dataclass, field
from datetime import datetime
from ...models.locale.enums.querytype import QueryType
from ...models.locale.enums.time_periods import TimePeriods
from ..locale.time_pattern import TimePattern
from ...models.locale.price.locale_price import LocalePrice
from .locale_query import LocaleQuery, ILocaleQuery


@dataclass
class Locale_Type:
    observed_peak: QueryType | None = None
    charged_peak: QueryType | None = None
    query_model: ILocaleQuery = field(default_factory=ILocaleQuery)
    query_service: QueryService | None = None
    price: LocalePrice = LocalePrice()
    free_charge_pattern: TimePattern | None = None
    peak_cycle: TimePeriods = TimePeriods.Hourly

    async def async_free_charge(self, mockdt: datetime | None = None) -> bool:
        if self.free_charge_pattern is None:
            return False
        now = mockdt or datetime.now()
        return await self.free_charge_pattern.async_valid(now)

    async def async_is_quarterly(self) -> bool:
        return self.peak_cycle == TimePeriods.QuarterHourly

    async def async_set_query_service(self):
        if self.query_service is not None:
            await self.query_model.async_set_query_service(self.query_service)
