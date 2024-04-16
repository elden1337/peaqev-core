from datetime import datetime
import logging
from ...models.locale.enums.price_type import PriceType
from ...models.locale.price.models.tiered_price import TieredPrice
from ..locale.locale_price_helpers import get_observed_peak

from ...models.locale.price.locale_price import LocalePrice
from .querytypes.queryservice import QueryService
from ...models.locale.peaks_model import PeaksModel
from ...models.locale.enums.sum_types import SumTypes
from ...models.locale.enums.time_periods import TimePeriods
from ...models.locale.sumcounter import SumCounter
from ...models.locale.queryproperties import QueryProperties
from .ilocale_query import ILocaleQuery

_LOGGER = logging.getLogger(__name__)

class LocaleQuery(ILocaleQuery):
    def __init__(
        self,
        sum_type: SumTypes,
        time_calc: TimePeriods,
        cycle: TimePeriods,
        sum_counter: SumCounter | None = None,
    ) -> None:
        self._peaks: PeaksModel = PeaksModel({})
        self._props = QueryProperties(sum_type, time_calc, cycle)
        self._sum_counter: SumCounter | None = sum_counter
        self._observed_peak_value: float = 0
        self._charged_peak_value: float = 0
        self._mock_dt: datetime | None = None
        self._price: LocalePrice = LocalePrice()

    @property
    def price(self) -> LocalePrice:
        return self._price
    
    @price.setter
    def price(self, value: LocalePrice):
        self._price = value

    def set_mock_dt(self, val: datetime | None):
        self._mock_dt = val

    @property
    def dt(self) -> datetime:
        return self._mock_dt if self._mock_dt is not None else datetime.now()

    @property
    def peaks(self) -> PeaksModel:
        if self._peaks.is_dirty:
            self._sanitize_values()
        return self._peaks

    @property
    def sum_counter(self) -> SumCounter:
        if self._sum_counter is not None:
            return self._sum_counter
        return SumCounter()

    @property
    def charged_peak(self) -> float:
        if self._peaks.is_dirty:
            self._sanitize_values()
        ret = self._charged_peak_value
        try:
            return round(ret, 2)
        except TypeError as t:
            _LOGGER.warning(t)
            return 0

    @charged_peak.setter
    def charged_peak(self, val):
        self._charged_peak_value = val

    @property
    def observed_peak(self) -> float:
        if self._peaks.is_dirty:
            self._sanitize_values()
        ret = (
            self.charged_peak
            if self._props.sumtype is SumTypes.Max
            else self.get_currently_obeserved_peak(self.dt)
        )
        try:
            return round(ret, 2)
        except TypeError as t:
            _LOGGER.warning(t)
            return 0

    @observed_peak.setter
    def observed_peak(self, val):
        self._observed_peak_value = val

    def get_currently_obeserved_peak(self, timestamp: datetime = datetime.now()) -> float:
        """gets the currently observed peak value for non-max type models. If daily max, override if the max registered today is higher."""
        ret = self._observed_peak_value

        if self.price.price_type == PriceType.Tiered:
            tiers:list[TieredPrice] = [s for s in self.price._values if isinstance(s, TieredPrice)]
            ret = get_observed_peak(self.price.price_type, [v for k, v in self._peaks.p.items()], tiers)

        if self.sum_counter.groupby == TimePeriods.Daily:
            if timestamp.day in [k[0] for k in self._peaks.p.keys()]:
                #_LOGGER.debug(f"exists as :{[v for k, v in self._peaks.p.items() if k[0] == timestamp.day][0]}. observed is {ret}. {self._peaks.p}. timestamp.day: {timestamp.day}")
                print(
                    f"exists as :{[v for k, v in self._peaks.p.items() if k[0] == timestamp.day][0]}. observed is {ret}. {self._peaks.p}. timestamp.day: {timestamp.day}")
                return max([v for k, v in self._peaks.p.items() if k[0] == timestamp.day][0], ret)
        print("returning observed", self._observed_peak_value)
        return ret

    def _sanitize_values(self):
        countX = lambda arr, x: len([a for a in arr if a[0] == x])
        if self.sum_counter.groupby == TimePeriods.Daily:
            duplicates = {}
            for k in self._peaks.p.keys():
                if countX(self._peaks.p.keys(), k[0]) > 1:
                    duplicates[k] = self._peaks.p[k]
            if len(duplicates):
                minkey = min(duplicates, key=duplicates.get) #type: ignore
                self._peaks.p.pop(minkey)
        while len(self._peaks.p) > self.sum_counter.counter:
            self._peaks.remove_min()
        self._peaks.is_dirty = False
        if self._props.sumtype is SumTypes.Max:
            self.charged_peak = self._peaks.max_value
        elif self._props.sumtype is SumTypes.Avg:
            self.observed_peak = self._peaks.min_value
            self.charged_peak = self._peaks.value_avg

    async def async_reset(self) -> None:
        await self._peaks.async_reset()
        self._observed_peak_value = 0
        self._charged_peak_value = 0

    async def async_set_query_service(self, service: QueryService) -> None:
        self._props.queryservice = service

    async def async_try_update(self, new_val, timestamp: datetime | None = None):
        _timestamp = timestamp or datetime.now()

        if not await self._props.queryservice.async_should_register_peak(dt=_timestamp):
            return
        _dt = (_timestamp.day, _timestamp.hour)
        if len(self.peaks.p) == 0:
            """first addition for this month"""
            await self.peaks.async_add_kv_pair(_dt, new_val)
            await self._peaks.async_set_month(_timestamp.month)
        elif _timestamp.month != self._peaks.m:
            """new month, reset"""
            await self.async_reset_values(new_val, _timestamp)
        else:
            await self.async_set_update_for_groupby(new_val, _dt)
        if len(self.peaks.p) > self.sum_counter.counter:
            await self.peaks.async_remove_min()
        await self.async_update_peaks()

    async def async_import_from_service(self, input_dict: dict) -> dict:
        """already good to go"""
        decorated_dict = {"m": datetime.now().month, "p": input_dict}
        await self.peaks.async_set_init_dict(decorated_dict)
        #await self.async_update_peaks()
        return decorated_dict

    async def async_set_update_for_groupby(self, new_val, dt):
        if self.sum_counter.groupby in [TimePeriods.Daily, TimePeriods.UnSet]:
            _datekeys = [k for k in self.peaks.p.keys() if dt[0] in k]
            #_LOGGER.debug(f"datekeys: {_datekeys}")
            if len(_datekeys):
                if new_val > self.peaks.p.get(_datekeys[0]):
                    await self.peaks.async_pop_key(_datekeys[0])
            await self.peaks.async_add_kv_pair(dt, new_val)
        elif self.sum_counter.groupby == TimePeriods.Hourly:
            if dt in self._peaks.p.keys():
                if new_val > self.peaks.p.get(dt):
                    await self.peaks.async_add_kv_pair(dt, new_val)
            else:
                await self.peaks.async_add_kv_pair(dt, new_val)

    async def async_update_peaks(self):
        if self._props.sumtype is SumTypes.Max:
            self.charged_peak = self._peaks.max_value
        elif self._props.sumtype is SumTypes.Avg:
            self.observed_peak = self._peaks.min_value
            self.charged_peak = self._peaks.value_avg
            print("updating peaks", self._peaks.p, self.observed_peak, self.charged_peak)

    async def async_reset_values(self, new_val, dt=datetime.now()):
        await self._peaks.async_clear()
        await self.async_try_update(new_val, dt)

    async def async_sanitize_values(self):
        countX = lambda arr, x: len([a for a in arr if a[0] == x])
        if self.sum_counter.groupby == TimePeriods.Daily:
            duplicates = {}
            for k in self._peaks.p.keys():
                if countX(self._peaks.p.keys(), k[0]) > 1:
                    duplicates[k] = self._peaks.p[k]
            if len(duplicates):
                minkey = min(duplicates, key=duplicates.get) #type: ignore
                self._peaks.p.pop(minkey)
        while len(self._peaks.p) > self.sum_counter.counter:
            await self._peaks.async_remove_min()
        self._peaks.is_dirty = False
        await self.async_update_peaks()
