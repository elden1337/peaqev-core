from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timedelta
from ..hoursselection_service_new.models.hour_price import HourPrice
#from ..hoursselection_service_new.models.hour_type import HourType
#from ..hoursselection_service_new.models.list_type import ListType
import copy

if TYPE_CHECKING:
    from .hourselection_service import HourSelectionService
#from typing import Tuple
from .models.max_min_model import MaxMinModel


class MaxMinCharge:
    def __init__(self, service: HourSelectionService, min_price: float | None) -> None:
        self.model = MaxMinModel(min_price=min_price)  # type: ignore
        self.parent = service
        self.active: bool = False
        self.overflow: bool = False
        self.current_peak: float | None = None

    @property
    def average_price(self) -> float | None:
        if not self.active:
            return None
        return self.model.caluclate_average_price(
            self.model.input_hours,
            self.total_charge,
            self.current_peak,
        )

    @property
    def original_average_price(self) -> float | None:
        return self.model.caluclate_average_price(
            self.parent.future_hours,
            self.original_total_charge,
            self.current_peak,
        )

    @property
    def total_charge(self) -> float | None:
        if not self.active:
            return None
        return self.model.calculate_total_charge(self.model.input_hours)

    @property
    def original_total_charge(self) -> float:
        return self.model.calculate_total_charge(self.parent.future_hours)

    def future_hours(self, dtmodel) -> list[HourPrice]:
        for hp in self.model.input_hours:
            hp.set_passed(dtmodel)
        ret = [hp for hp in self.model.input_hours if not hp.passed]
        return sorted(ret, key=lambda x: x.dt)

    async def async_update(
        self,
        avg24,
        peak,
        max_desired: float,
        session_energy: float | None = None,
        car_connected: bool = False,
    ) -> None:
        if not car_connected:
            await self.async_setup(max_charge=peak)
        _session = session_energy or 0
        _desired = max_desired - _session
        _avg24 = round((avg24 / 1000), 1)
        self.model.expected_hourly_charge = max(peak - _avg24, 0)
        self.current_peak = peak
        if _desired >= self.original_total_charge:
            self.overflow = True
            self.get_hours()
            return
        else:
            self.overflow = False
            self.select_hours_for_charge(
                copy.deepcopy(self.parent.future_hours), _desired
            )

    def select_hours_for_charge(
        self, hours: list[HourPrice], desired_charge: float
    ) -> None:
        _original_charge = self._get_charge_sum(hours)
        _total_charge: float = 0
        _desired: float = min([desired_charge, _original_charge])
        while _total_charge < _desired:
            hours.sort(key=lambda x: (x.price,x.dt))
            for hour in hours:
                if any([hour.passed, hour.permittance == 0, _total_charge >= _desired]):
                    hour.permittance = 0
                    continue
                _hour_charge = hour.permittance * self.model.expected_hourly_charge
                _perm = min(
                    1,
                    max(
                        (_desired - _total_charge) / self.model.expected_hourly_charge,
                        0,
                    ),
                )
                _total_charge += _hour_charge * _perm
                hour.permittance = round(_perm, 2)
                if self._get_charge_sum(hours) <= desired_charge:
                    break
        self.model.input_hours = hours

    def _get_charge_sum(self, hours: list[HourPrice]) -> float:
        return sum(
            [
                hour.permittance * self.model.expected_hourly_charge
                for hour in hours
                if not hour.passed
            ]
        )

    def _set_expected_charge(self, desired, peak, avg24) -> float:
        return (desired - self.total_charge) / (peak - avg24)

    async def async_sum_charge(self, avg24, peak) -> float:
        total = 0
        for k in self.model.input_hours:
            total += (peak - avg24) * k.permittance
        return total

    async def async_setup(
        self,
        max_charge: float,
    ) -> None:
        if max_charge == 0:
            self.active = False
            return
        if not self.active:
            self.get_hours()
            self.active = True

    def get_hours(self) -> None:
        self.model.input_hours = copy.deepcopy(self.parent.future_hours)
        # self.model.original_input_hours = copy.deepcopy(self.model.input_hours)
