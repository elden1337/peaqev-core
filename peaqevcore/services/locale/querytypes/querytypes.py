from datetime import date, datetime, time
import logging

from ....models.locale.enums.querytype import QueryType

from .queryservice import QueryService
from ....models.locale.peaks_model import PeaksModel
from ....models.locale.enums.sum_types import SumTypes
from ....models.locale.enums.time_periods import TimePeriods
from ....models.locale.sumcounter import SumCounter
from ....models.locale.queryproperties import QueryProperties

_LOGGER = logging.getLogger(__name__)


class LocaleQuery:
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

    def reset(self) -> None:
        self._peaks.reset()
        self._observed_peak_value = 0
        self._charged_peak_value = 0

    # def set_query_service(self, service: QueryService) -> None:
    #     self._props.queryservice = service

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
        return round(ret, 2)

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
            else self._observed_peak_value
        )
        return round(ret, 2)

    @observed_peak.setter
    def observed_peak(self, val):
        self._observed_peak_value = val

    def _sanitize_values(self):
        countX = lambda arr, x: len([a for a in arr if a[0] == x])
        if self.sum_counter.groupby == TimePeriods.Daily:
            duplicates = {}
            for k in self._peaks.p.keys():
                if countX(self._peaks.p.keys(), k[0]) > 1:
                    duplicates[k] = self._peaks.p[k]
            if len(duplicates):
                minkey = min(duplicates, key=duplicates.get)
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

    async def async_set_update_for_groupby(self, new_val, dt):
        if self.sum_counter.groupby in [TimePeriods.Daily, TimePeriods.UnSet]:
            # todo: check this if it breaks the updatehour
            _datekeys = [k for k in self.peaks.p.keys() if dt[0] in k]
            if len(_datekeys):
                if new_val > self.peaks.p.get(_datekeys[0]):
                    await self.peaks.async_pop_key(_datekeys[0])
                    await self.peaks.async_add_kv_pair(dt, new_val)
            # todo: check this if it breaks the updatehour
            else:
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
                minkey = min(duplicates, key=duplicates.get)
                self._peaks.p.pop(minkey)
        while len(self._peaks.p) > self.sum_counter.counter:
            await self._peaks.async_remove_min()
        self._peaks.is_dirty = False
        await self.async_update_peaks()


QUERYTYPES = {
    QueryType.AverageOfThreeHours: LocaleQuery(
        sum_type=SumTypes.Avg,
        time_calc=TimePeriods.Hourly,
        cycle=TimePeriods.Monthly,
        sum_counter=SumCounter(counter=3, groupby=TimePeriods.Hourly),
    ),
    QueryType.AverageOfThreeDays: LocaleQuery(
        sum_type=SumTypes.Avg,
        time_calc=TimePeriods.Hourly,
        cycle=TimePeriods.Monthly,
        sum_counter=SumCounter(counter=3, groupby=TimePeriods.Daily),
    ),
    QueryType.Max: LocaleQuery(
        sum_type=SumTypes.Max, time_calc=TimePeriods.Hourly, cycle=TimePeriods.Monthly
    ),
    QueryType.AverageOfFiveDays: LocaleQuery(
        sum_type=SumTypes.Avg,
        time_calc=TimePeriods.Hourly,
        cycle=TimePeriods.Monthly,
        sum_counter=SumCounter(counter=5, groupby=TimePeriods.Daily),
    ),
}
