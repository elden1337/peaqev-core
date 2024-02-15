from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timedelta

from .models.permittance_type import PermittanceType
from .models.hour_type import HourType
from ..hoursselection_service_new.models.hour_price import HourPrice
import copy
if TYPE_CHECKING:
    from .hourselection_service import HourSelectionService
from .models.max_min_model import MaxMinModel


class MaxMinHourCap:
    def __init__(self) -> None:
        self._car_connected: bool = False
        self._allow_calculate_cap: bool = False
        self._current_cap: datetime = datetime.max

    @property
    def do_calculate_cap(self) -> bool:
        return self._allow_calculate_cap

    @property
    def car_connected(self) -> bool:
        return self._car_connected
    
    @car_connected.setter
    def car_connected(self, val: bool) -> None:
        if val != self._car_connected:
            self._allow_calculate_cap = True
        self._car_connected = val

    def cap(self, hours: list[HourPrice]) -> datetime:
        if self._allow_calculate_cap or min([x.dt for x in hours if not x.passed]) >= self._current_cap:
            current_hour = min([x.dt for x in hours if not x.passed])
            end_hour = datetime.max
            match current_hour.hour:
                case 9|10|11|12|13|14|15|16|17|18|19|20|21|22|23:
                    end_hour = (current_hour + timedelta(days=1)).replace(hour=9)
                case 0|1|2|3|4|5|6|7|8:
                    end_hour = (current_hour).replace(hour=18)
            self._current_cap = end_hour
            self._allow_calculate_cap = False
        return self._current_cap


class MaxMinCharge:
    def __init__(self, service: HourSelectionService, min_price: float | None) -> None:
        self.model = MaxMinModel(min_price=min_price)  # type: ignore
        self.hour_cap = MaxMinHourCap()
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
        limiter: float = 0.0
    ) -> None:
        self.hour_cap.car_connected = car_connected
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
            if self._price_is_too_similar(limiter):
                self.overflow = True
                self.get_hours()
                return

    def _price_is_too_similar(self, limiter: float) -> bool:
        original = getattr(self, "original_average_price",0)
        adjusted = getattr(self, "average_price",0)
        if original > 0 and adjusted > 0:
            return max(original,adjusted) - min(original,adjusted) < limiter
        return False

    def _cap_future_hours(self, hours: list[HourPrice]) -> list[HourPrice]:
        if self.hour_cap.do_calculate_cap:
            hours = [setattr(hour, 'permittance_type', PermittanceType.Regular) or hour for hour in hours]
        cap = self.hour_cap.cap(hours)
        maxmin_hours = [setattr(x, 'permittance_type', PermittanceType.MaxMin) or x for x in hours if x.dt <= cap]
        return maxmin_hours

    def select_hours_for_charge(
        self, hours: list[HourPrice], desired_charge: float
    ) -> None:
        _capped_hours = self._cap_future_hours(hours)
        _original_charge = self._get_charge_sum(_capped_hours)
        _total_charge: float = 0
        _desired: float = min([desired_charge, _original_charge])
        while _total_charge < _desired:
            _capped_hours.sort(key=lambda x: (x.price,x.dt))
            for hour in _capped_hours:
                if any([hour.passed, hour.permittance == 0, _total_charge >= _desired, hour.hour_type is HourType.AboveMax]):
                    hour.permittance = 0
                    continue
                _hour_charge = hour.permittance * self.model.expected_hourly_charge
                _perm = min(1,max((_desired - _total_charge) / self.model.expected_hourly_charge,0))
                _total_charge += _hour_charge * _perm
                hour.permittance = round(_perm, 2)
                if self._get_charge_sum(_capped_hours) <= desired_charge:
                    break
        self.model.input_hours = self._combine_hour_lists(hours, _capped_hours)

    def _combine_hour_lists(self, hours: list[HourPrice], capped_hours: list[HourPrice]) -> list[HourPrice]:
        capped_hours_dict = {x.dt: x for x in capped_hours}
        for i, hour in enumerate(hours):
            if hour.dt in capped_hours_dict:
                hours[i] = capped_hours_dict[hour.dt]
        return hours

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
            self.active = True
            self.get_hours()

    def get_hours(self) -> None:
        if self.active:
            self.model.input_hours = copy.deepcopy(self.parent.future_hours)
        # self.model.original_input_hours = copy.deepcopy(self.model.input_hours)
