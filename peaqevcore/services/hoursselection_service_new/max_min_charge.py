from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from .hourselection_service import HourSelectionService
from typing import Tuple
from .models.max_min_model import MaxMinModel

MINIMUM_DIFFERENCE = 0.1


class MaxMinCharge:
    def __init__(self, service: HourSelectionService, min_price: float | None) -> None:
        self.model = MaxMinModel(min_price=min_price)  # type: ignore
        self.parent = service
        self.active: bool = False

    @property
    def average_price(self) -> float | None:
        if not self.active:
            return None
        return self.model.caluclate_average_price(
            self.model.input_hours, self.total_charge
        )

    @property
    def original_average_price(self) -> float | None:
        return self.model.caluclate_average_price(
            self.model.original_input_hours, self.original_total_charge
        )

    @property
    def total_charge(self) -> float | None:
        if not self.active:
            return None
        return self.model.calculate_total_charge(self.model.input_hours)

    @property
    def original_total_charge(self) -> float:
        return self.model.calculate_total_charge(self.parent.future_hours)

    @property
    def non_hours(self) -> list:
        return [
            hp.dt
            for hp in self.model.input_hours
            if hp.permittance == 0 and hp.dt >= self.parent.dtmodel.dt
        ]

    @property
    def dynamic_caution_hours(self) -> dict:
        return {
            hp.dt: hp.permittance
            for hp in self.model.input_hours
            if 0 < hp.permittance < 1 and hp.dt >= self.parent.dtmodel.dt
        }

    async def async_allow_decrease(self, car_connected: bool | None = None) -> bool:
        if car_connected is not None:
            return all(
                [
                    # not car_connected,
                    len([v for v in self.model.input_hours if v.permittance > 0])
                    != 1,
                ]
            )
        return len([v for v in self.model.input_hours if v.permittance > 0]) != 1

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

    #     self._set_earliest_cheaphour()

    # def _set_earliest_cheaphour(self) -> None:
    #     charge_hours = [h for h in self.model.input_hours if h.permittance > 0]
    #     if charge_hours:
    #         for i in enumerate(charge_hours):
    #             earlier = [
    #                 h for h in charge_hours if h.dt < i[1].dt and i[1].price == h.price
    #             ]
    #             if earlier:
    #                 i[1].permittance = 0.0
    #                 earlier[0].permittance = 1
    # todo: fix this to get sequence of hours

    async def async_increase_decrease(
        self, desired, avg24, peak, allow_decrease: bool
    ) -> None:
        for i in range(len(self.model.original_input_hours)):
            _load = self.total_charge - desired
            if _load > MINIMUM_DIFFERENCE and allow_decrease:
                await self.async_decrease()
            elif _load < MINIMUM_DIFFERENCE * -1:
                expected_charge = self._set_expected_charge(desired, peak, avg24)
                await self.async_increase(expected_charge)
            if any(
                [
                    abs(_load) < MINIMUM_DIFFERENCE,
                    (self.total_charge or 0) > self.original_total_charge,
                    (self.average_price or 0) > (self.original_average_price or 0),
                ]
            ):
                break

    def _set_expected_charge(self, desired, peak, avg24) -> float:
        return (desired - self.total_charge) / (peak - avg24)

    async def async_initial_charge(self, avg24, peak) -> float:
        _avg24 = round((avg24 / 1000), 1)
        self.model.expected_hourly_charge = peak - _avg24
        total = 24 * (peak - _avg24)  # todo: fix 24 to be dynamic
        total -= len(self.non_hours) * (peak - _avg24)
        total -= sum(self.dynamic_caution_hours.values()) * (peak - _avg24)
        return total

    async def async_sum_charge(self, avg24, peak) -> float:
        total = 0
        for k in self.model.input_hours:
            total += (peak - avg24) * k.permittance
        return total

    async def async_decrease(self):
        filtered_hours = [
            hour for hour in self.model.input_hours if 0 < hour.permittance <= 1
        ]
        if filtered_hours:
            max_hour = max(filtered_hours, key=lambda hour: hour.price)
            max_key = self.model.input_hours.index(max_hour)
            self.model.input_hours[max_key].permittance = 0.0

    async def async_increase(self, expected_charge):
        filtered_hours = [
            hour for hour in self.model.input_hours if 0 < hour.permittance <= 1
        ]
        if filtered_hours:
            min_hour = min(filtered_hours, key=lambda hour: hour.price)
            min_key = self.model.input_hours.index(min_hour)
            original_permittance = [
                h for h in self.model.original_input_hours if h.dt == min_hour.dt
            ][0].permittance
            self.model.input_hours[min_key].permittance = min(
                min(1, expected_charge), original_permittance
            )

    def _service_caution_hours(self) -> dict:
        return {
            hp.dt: hp.permittance
            for hp in self.parent.model.hours_prices
            if not hp.passed and 0.0 < hp.permittance < 1.0
        }

    def _service_non_hours(self) -> list:
        return [
            hp.dt
            for hp in self.parent.model.hours_prices
            if not hp.passed and hp.permittance == 0.0
        ]

    async def async_setup(
        self,
        max_charge: float,
        non_hours: list | None = None,
        dynamic_caution_hours: dict | None = None,
        prices: list | None = None,
        prices_tomorrow: list | None = None,
    ) -> None:
        if max_charge == 0:
            self.active = False
            return
        hour = self.parent.dtmodel.hour
        dt = self.parent.dtmodel.dt
        _non_hours = self._service_non_hours() if non_hours is None else non_hours
        _dynamic_caution_hours = (
            self._service_caution_hours()
            if dynamic_caution_hours is None
            else dynamic_caution_hours
        )
        _prices = self.parent.model.prices_today if prices is None else prices
        _prices_tomorrow = (
            self.parent.model.prices_tomorrow
            if prices_tomorrow is None
            else prices_tomorrow
        )

        self.model.input_hours = self.parent.future_hours
        self.model.original_input_hours = self.model.input_hours.copy()
        self.active = True
