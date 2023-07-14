from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ....models.hourselection.hourselection_options import HourSelectionOptions
from dataclasses import dataclass, field
from .hour_price import HourPrice
from datetime import date, datetime, time, timedelta
from .list_type import ListType
from ...hourselection.hourselectionservice.hoursselection_helpers import convert_none_list
from ..offset_dict import get_offset_dict, set_offset_dict


@dataclass
class HourSelectionServiceModel:
    _prices_today: list[float] = field(default_factory=list)
    _prices_tomorrow: list[float] = field(default_factory=list)
    _hours_prices: list[HourPrice] = field(default_factory=list)
    offset_dict: dict[datetime, dict] = field(default_factory=dict)
    adjusted_average: float | None = None
    use_quarters: bool = False

    @property
    def hours_prices(self) -> list[HourPrice]:
        return self._hours_prices

    @hours_prices.setter
    def hours_prices(self, val: list[HourPrice]) -> None:
        if val is not None:
            if len(val) > 0:
                self._hours_prices = val
                self._hours_prices.sort(key=lambda x: x.dt)
        else:
            self._hours_prices = []

    @property
    def prices_today(self) -> list:
        return self._prices_today

    @prices_today.setter
    def prices_today(self, val):
        self._prices_today = val
        if self._prices_today == self.prices_tomorrow:
            self.prices_tomorrow = []

    @property
    def prices_tomorrow(self) -> list:
        return self._prices_tomorrow

    @prices_tomorrow.setter
    def prices_tomorrow(self, val):
        ret = convert_none_list(val)
        self._prices_tomorrow = ret

    def set_hourprice_lists(self, prices:list, prices_tomorrow:list, service_options:HourSelectionOptions, datum:date, datum_tomorrow:date, is_passed_func:Callable) -> None:
        self.set_hourprice_list(prices, service_options, datum, is_passed_func)
        self.set_hourprice_list(prices_tomorrow, service_options, datum_tomorrow, is_passed_func)
        self.hours_prices.sort(key=lambda x:x.dt)

    def set_hourprice_list(
        self,
        prices: list,
        service_options: HourSelectionOptions,
        datum: date,
        is_passed_func: Callable,
    ) -> None:
        ret = []
        for idx, p in enumerate(prices):  # type: ignore
            assert isinstance(p, (float, int))
            hour = int(idx / 4) if self.use_quarters else idx
            quarter = idx % 4 if self.use_quarters else 0
            rret = HourPrice(
                dt=self._get_dt(datum, hour, quarter),
                quarter=quarter,
                price=p,
                passed=is_passed_func(datum, hour, quarter),
                hour_type=HourPrice.set_hour_type(
                    service_options.absolute_top_price, service_options.min_price, p
                ),
                list_type=ListType.Quarterly if self.use_quarters else ListType.Hourly,
            )
            if rret not in self.hours_prices:
                ret.append(rret)
        if len(self.hours_prices) > 0:
            self.hours_prices.extend(ret)
        else:
            self.hours_prices = ret

    def get_offset_dict(self, dt_date: datetime) -> dict:
        return get_offset_dict(self.offset_dict, dt_date)

    def set_offset_dict(self, prices: list[float], day: date) -> None:
        if all(
            [
                day in self.offset_dict.keys(),
                day - timedelta(days=1) in self.offset_dict.keys(),
            ]
        ):
            return
        self.offset_dict = set_offset_dict(prices, day)

    def get_future_hours(self, dtmodel) -> list[HourPrice]:
        for hp in self.hours_prices:
            hp.set_passed(dtmodel)
        return [hp for hp in self.hours_prices if not hp.passed]

    @staticmethod
    def _get_dt(datum: date, hour: int, quarter: int) -> datetime:
        return datetime.combine(
            datum, time(hour=hour, minute=quarter * 15, second=0, microsecond=0)
        )