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
from abc import abstractmethod


class Locale_Type:
    _observed_peak = None
    _charged_peak = None
    _query_model: ILocaleQuery = field(default_factory=ILocaleQuery)
    _query_service = None
    _price: LocalePrice = LocalePrice()
    _free_charge_pattern = None
    _peak_cycle: TimePeriods = TimePeriods.Hourly

    @property
    @abstractmethod
    def observed_peak(self) -> QueryType:
        return self._observed_peak

    @observed_peak.setter
    @abstractmethod
    def observed_peak(self, value: QueryType):
        self._observed_peak = value

    @property
    @abstractmethod
    def charged_peak(self) -> QueryType:
        return self._charged_peak

    @charged_peak.setter
    @abstractmethod
    def charged_peak(self, value: QueryType):
        self._charged_peak = value

    @property
    @abstractmethod
    def query_model(self) -> ILocaleQuery:
        return self._query_model

    @query_model.setter
    @abstractmethod
    def query_model(self, value: ILocaleQuery):
        self._query_model = value

    @property
    @abstractmethod
    def query_service(self) -> QueryService:
        return self._query_service

    @query_service.setter
    @abstractmethod
    def query_service(self, value: QueryService):
        self._query_service = value

    @property
    @abstractmethod
    def price(self) -> LocalePrice:
        return self._price

    @price.setter
    @abstractmethod
    def price(self, value: LocalePrice):
        self._price = value

    @property
    @abstractmethod
    def free_charge_pattern(self) -> TimePattern:
        return self._free_charge_pattern

    @free_charge_pattern.setter
    @abstractmethod
    def free_charge_pattern(self, value: TimePattern):
        self._free_charge_pattern = value

    @property
    def peak_cycle(self) -> TimePeriods:
        return self._peak_cycle

    @peak_cycle.setter
    def peak_cycle(self, value: TimePeriods):
        self._peak_cycle = value

    async def async_free_charge(self, mockdt: datetime | None = None) -> bool:
        if self.free_charge_pattern is None:
            return False
        now = mockdt or datetime.now()
        return await self.free_charge_pattern.async_valid(now)

    async def async_is_quarterly(self) -> bool:
        return self.peak_cycle == TimePeriods.QuarterHourly

    def is_quarterly(self) -> bool:
        return self.peak_cycle == TimePeriods.QuarterHourly

    async def async_set_query_service(self):
        if self.query_service is not None:
            await self.query_model.async_set_query_service(self.query_service)
