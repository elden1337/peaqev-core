from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..hoursselection import Hoursselection
from typing import Tuple
from ....models.hourselection.max_min_model import MaxMinModel

MINIMUM_DIFFERENCE = 0.1


class MaxMinCharge:
    def __init__(self, hoursselection: Hoursselection, min_price: float | None) -> None:
        self.model = MaxMinModel(min_price=min_price)
        self.parent = hoursselection
        self.active: bool = False

    @property
    def total_charge(self) -> float:
        return self.model.total_charge

    @property
    def average_price(self) -> float | None:
        return self.model.average_price

    @property
    def original_total_charge(self) -> float:
        return self.model.original_total_charge

    @property
    def original_average_price(self) -> float | None:
        return self.model.original_average_price

    @property
    def non_hours(self) -> list:
        return [k for k, v in self.model.input_hours.items() if v[1] == 0]

    @property
    def dynamic_caution_hours(self) -> dict:
        return {k: v[1] for k, v in self.model.input_hours.items() if 0 < v[1] < 1}

    async def async_allow_decrease(self, car_connected: bool | None = None) -> bool:
        if car_connected is not None:
            return all(
                [
                    not car_connected,
                    len([k for k, v in self.model.input_hours.items() if v[1] > 0])
                    != 1,
                ]
            )
        return len([k for k, v in self.model.input_hours.items() if v[1] > 0]) != 1

    async def async_update(
        self,
        avg24,
        peak,
        max_desired: float,
        session_energy: float | None = None,
        car_connected: bool | None = None,
    ) -> None:
        allow_decrease: bool = False
        if await self.async_allow_decrease(car_connected):
            allow_decrease = True
            await self.async_setup(max_charge=peak)
        _session = session_energy or 0
        _desired = max_desired - _session
        _avg24 = round((avg24 / 1000), 1)
        self.model.expected_hourly_charge = peak - _avg24
        await self.async_increase_decrease(_desired, _avg24, peak, allow_decrease)

    async def async_increase_decrease(
        self, desired, avg24, peak, allow_decrease: bool
    ) -> None:
        for i in range(len(self.model.original_input_hours.items())):
            _load = self.total_charge - desired
            if _load > MINIMUM_DIFFERENCE and allow_decrease:
                await self.async_decrease()
            elif _load < MINIMUM_DIFFERENCE * -1:
                expected_charge = (desired - self.total_charge) / (peak - avg24)
                await self.async_increase(expected_charge)
            if abs(_load) < MINIMUM_DIFFERENCE:
                break

    async def async_initial_charge(self, avg24, peak) -> float:
        _avg24 = round((avg24 / 1000), 1)
        self.model.expected_hourly_charge = peak - _avg24
        total = 24 * (peak - _avg24)  # todo: fix 24 to be dynamic
        total -= len(self.non_hours) * (peak - _avg24)
        total -= sum(self.dynamic_caution_hours.values()) * (peak - _avg24)
        return total

    async def async_sum_charge(self, avg24, peak) -> float:
        total = 0
        for k, v in self.model.input_hours.items():
            total += (peak - avg24) * v[1]
        return total

    async def async_decrease(self):
        max_key = max(
            self.model.input_hours,
            key=lambda k: self.model.input_hours[k][0]
            if self.model.input_hours[k][1] != 0
            and self.model.input_hours[k][0] > self.model.min_price
            else -1,
        )
        self.model.input_hours[max_key] = (self.model.input_hours[max_key][0], 0)

    async def async_increase(self, expected_charge):
        min_key = min(
            self.model.input_hours,
            key=lambda k: self.model.input_hours[k][0]
            if self.model.input_hours[k][1] < 1
            and self.model.original_input_hours[k][1] > 0
            else 999,
        )
        self.model.input_hours[min_key] = (
            self.model.input_hours[min_key][0],
            min(min(1, expected_charge), self.model.original_input_hours[min_key][1]),
        )

    async def async_setup(
        self,
        max_charge: float,
        non_hours: list | None = None,
        dynamic_caution_hours: dict | None = None,
        prices: list | None = None,
        prices_tomorrow: list | None = None,
        mock_hour: int | None = None,
    ) -> None:
        if max_charge == 0:
            self.active = False
            return
        hour = (
            mock_hour
            if mock_hour is not None
            else await self.parent.service.async_set_hour()
        )
        _non_hours = self.parent.internal_non_hours if non_hours is None else non_hours
        _dynamic_caution_hours = (
            self.parent.internal_dynamic_caution_hours
            if dynamic_caution_hours is None
            else dynamic_caution_hours
        )
        _prices = self.parent.prices if prices is None else prices
        _prices_tomorrow = (
            self.parent.prices_tomorrow if prices_tomorrow is None else prices_tomorrow
        )
        ret_today, ret_tomorrow = await self.async_loop_nonhours(
            hour, _non_hours, _prices, _prices_tomorrow
        )
        await self.async_loop_caution_hours(
            hour,
            _dynamic_caution_hours,
            _prices,
            _prices_tomorrow,
            ret_today,
            ret_tomorrow,
        )
        await self.async_add_available_hours(
            hour, _prices, _prices_tomorrow, ret_today, ret_tomorrow
        )
        self.model.input_hours = await self.async_sort_dicts(ret_today, ret_tomorrow)
        self.model.original_input_hours = self.model.input_hours.copy()
        self.active = True

    @staticmethod
    async def async_add_available_hours(
        hour: int,
        prices: list,
        prices_tomorrow: list,
        ret_today: dict,
        ret_tomorrow: dict,
    ) -> None:
        _hour = hour
        _range = 24 if len(prices_tomorrow) > 0 else len(prices) - hour
        for i in range(_range):
            if _hour < hour and _hour not in ret_tomorrow.keys():
                ret_tomorrow[_hour] = (prices_tomorrow[_hour], 1)
                # todo: must test this without valid prices tomorrow.
            elif _hour >= hour and _hour not in ret_today.keys():
                ret_today[_hour] = (prices[_hour], 1)
            _hour += 1
            if _hour > 23:
                _hour = 0

    @staticmethod
    async def async_loop_caution_hours(
        hour: int,
        caution_hours: dict,
        prices: list,
        prices_tomorrow: list,
        ret_today: dict,
        ret_tomorrow: dict,
    ) -> None:
        for k, v in caution_hours.items():
            if k >= hour:
                ret_today[k] = (prices[k], v)
            elif len(prices_tomorrow) > 0:
                ret_tomorrow[k] = (prices_tomorrow[k], v)

    @staticmethod
    async def async_loop_nonhours(
        hour: int, non_hours: list, prices: list, prices_tomorrow: list
    ) -> Tuple[dict, dict]:
        ret_today = {}
        ret_tomorrow = {}
        for n in non_hours:
            if n >= hour:
                ret_today[n] = (prices[n], 0)
            elif len(prices_tomorrow) > 0:
                ret_tomorrow[n] = (prices_tomorrow[n], 0)
        return ret_today, ret_tomorrow

    @staticmethod
    async def async_sort_dicts(ret_today: dict, ret_tomorrow: dict) -> dict:
        ret = {}
        for k in sorted(ret_today.keys()):
            ret[k] = ret_today[k]
        for k in sorted(ret_tomorrow.keys()):
            ret[k] = ret_tomorrow[k]
        return ret
