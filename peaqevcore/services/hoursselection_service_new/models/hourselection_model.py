from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ....models.hourselection.hourselection_options import HourSelectionOptions
from dataclasses import dataclass, field
from .hour_price import HourPrice
from datetime import date, datetime, time, timedelta
from .list_type import ListType
from ..offset_dict import get_offset_dict, set_offset_dict


@dataclass
class HourSelectionModel:
    prices_today: list[float] = field(default_factory=list)
    prices_tomorrow: list[float] = field(default_factory=list)
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

    @staticmethod
    def _get_dt(datum: date, hour: int, quarter: int) -> datetime:
        return datetime.combine(
            datum, time(hour=hour, minute=quarter * 15, second=0, microsecond=0)
        )

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
