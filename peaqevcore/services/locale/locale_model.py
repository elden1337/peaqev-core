from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...services.locale.querytypes.queryservice import QueryService
from dataclasses import field
from datetime import datetime
from ...models.locale.enums.querytype import QueryType
from ...models.locale.enums.time_periods import TimePeriods
from ..locale.time_pattern import TimePattern
from ...models.locale.price.locale_price import LocalePrice
from .ilocale_query import ILocaleQuery

class Locale_Type:
    _observed_peak = None
    _charged_peak = None
    _query_model: ILocaleQuery = field(default_factory=ILocaleQuery)
    _query_service = None
    _price: LocalePrice = LocalePrice()
    _free_charge_pattern = None
    _peak_cycle: TimePeriods = TimePeriods.Hourly
    _aux_levels: list = field(default_factory=lambda: [])
    _holidays: list = field(default_factory=lambda: [])

    @property
    def observed_peak(self) -> QueryType:
        return self._observed_peak #type: ignore

    @observed_peak.setter
    def observed_peak(self, value: QueryType):
        self._observed_peak = value

    @property
    def charged_peak(self) -> QueryType:
        return self._charged_peak #type: ignore

    @charged_peak.setter
    def charged_peak(self, value: QueryType):
        self._charged_peak = value

    @property
    def query_model(self) -> ILocaleQuery:
        return self._query_model

    
    @query_model.setter
    def query_model(self, value: ILocaleQuery):
        self._query_model = value

    @property
    def query_service(self) -> QueryService:
        return self._query_service #type: ignore

    @query_service.setter    
    def query_service(self, value: QueryService):
        self._query_service = value

    @property
    def price(self) -> LocalePrice:
        return self._price

    @price.setter
    def price(self, value: LocalePrice):
        self._price = value

    @property    
    def free_charge_pattern(self) -> TimePattern:
        return self._free_charge_pattern #type: ignore

    @free_charge_pattern.setter    
    def free_charge_pattern(self, value: TimePattern):
        self._free_charge_pattern = value

    @property
    def peak_cycle(self) -> TimePeriods:
        return self._peak_cycle

    @peak_cycle.setter
    def peak_cycle(self, value: TimePeriods):
        self._peak_cycle = value

    @property
    def aux_levels(self) -> list:
        return self._aux_levels

    @property
    def holidays(self) -> list:
        return self._holidays

    async def async_free_charge(self, mockdt: datetime | None = None) -> bool:
        if self.free_charge_pattern is None:
            return False
        now = mockdt or datetime.now()
        if self._date_matches_holiday(now):
            return True
        return await self.free_charge_pattern.async_valid(now)

    def _date_matches_holiday(self, dt: datetime) -> bool:
        date_dict = self._parse_holidays_list()
        if dt.month not in date_dict.keys():
            return False
        if dt.day not in date_dict[dt.month]:
            return False
        return True

    def _parse_holidays_list(self) -> dict:
        if not len(self._holidays):
            return {}
        ret = {}
        for val in self._holidays:
            splitval = str(val).split('.')
            if splitval[0] not in ret.keys():
                ret[splitval[0]] = []
            ret[splitval[0]].append(splitval[1])
        return ret

    async def async_is_quarterly(self) -> bool:
        return self.peak_cycle == TimePeriods.QuarterHourly

    def is_quarterly(self) -> bool:
        return self.peak_cycle == TimePeriods.QuarterHourly

    async def async_set_query_service(self):
        if self.query_service is not None:
            await self.query_model.async_set_query_service(self.query_service)
        self.query_model.price = self.price
