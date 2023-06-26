from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ....models.hourselection.hourselection_options import HourSelectionOptions
from dataclasses import dataclass, field
from .hour_price import HourPrice
from datetime import date, datetime, time
from .list_type import ListType


@dataclass
class HourSelectionModel:
    prices_today: list[float] = field(default_factory=list)
    prices_tomorrow: list[float] = field(default_factory=list)
    _hours_prices: list[HourPrice] = field(default_factory=list)
    adjusted_average: float | None = None

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
        is_quarterly: bool,
        datum: date,
        is_passed_func: Callable,
    ) -> None:
        ret = []
        for idx, p in enumerate(prices):  # type: ignore
            assert isinstance(p, (float, int))
            hour = int(idx / 4) if is_quarterly else idx
            quarter = idx % 4 if is_quarterly else 0
            ret.append(
                HourPrice(
                    dt=self._get_dt(datum, hour, quarter),
                    quarter=quarter,
                    price=p,
                    passed=is_passed_func(datum, hour, quarter),
                    hour_type=HourPrice.set_hour_type(
                        service_options.absolute_top_price, service_options.min_price, p
                    ),
                    list_type=ListType.Quarterly if is_quarterly else ListType.Hourly,
                )
            )
        if len(self.hours_prices) > 0:
            self.hours_prices.extend(ret)
        else:
            self.hours_prices = ret

    @staticmethod
    def _get_dt(datum: date, hour: int, quarter: int) -> datetime:
        return datetime.combine(
            datum, time(hour=hour, minute=quarter * 15, second=0, microsecond=0)
        )
