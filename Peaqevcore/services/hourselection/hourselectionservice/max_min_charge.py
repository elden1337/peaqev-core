from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class MaxMinModel:
    input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    original_input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    total_charge: float = 0


class MaxMinCharge:
    def __init__(self) -> None:
        self.model = MaxMinModel()

    @property
    def total_charge(self) -> float:
        return self.model.total_charge
    
    @total_charge.setter
    def total_charge(self, value: float) -> None:
        self.model.total_charge = round(value,1)

    @property
    def non_hours(self) -> list:
        """non hours"""
        return [k for k, v in self.model.input_hours.items() if v[1] == 0]
    
    @property
    def caution_hours(self) -> dict:
        """dynamic caution hours"""
        return {k: v[1] for k, v in self.model.input_hours.items() if 0 < v[1] < 1}

    async def async_update(self, avg24, peak, max_desired) -> None:
        _avg24 = round(avg24,1)
        for i in range(len(self.model.original_input_hours.items())):
            _sum = await self.async_sum_charge(_avg24, peak)
            if _sum - max_desired > 0.05:
                await self.async_decrease()
            elif _sum - max_desired < -0.05:
                expected_charge = round((max_desired-_sum)/(peak-_avg24),2)
                await self.async_increase(expected_charge)
            if abs(_sum - max_desired) < 0.05:
                break            
        self.total_charge = await self.async_sum_charge(_avg24, peak)

    async def async_initial_charge(self, avg24, peak) -> float:
        total=24*(peak-avg24)
        total -= len(self.non_hours)*(peak-avg24)
        total -= sum(self.caution_hours.values())*(peak-avg24)
        return total

    async def async_sum_charge(self, avg24, peak) -> float:
        total=0
        for k, v in self.model.input_hours.items():
            total += (peak-avg24)*v[1]
        return total

    async def async_decrease(self):
        max_key = max(
            self.model.input_hours, 
            key=lambda k: self.model.input_hours[k][0] if self.model.input_hours[k][1] != 0 else -1
            )
        self.model.input_hours[max_key] = (self.model.input_hours[max_key][0], 0)

    async def async_increase(self, expected_charge):
        min_key = min(
            self.model.input_hours, 
            key=lambda k: self.model.input_hours[k][0] if self.model.input_hours[k][1] < 1 and self.model.original_input_hours[k][1] > 0 else 999
            )
        self.model.input_hours[min_key] = (self.model.input_hours[min_key][0], min(
            min(1, expected_charge), 
            self.model.original_input_hours[min_key][1]
            ))

    async def async_make_hours(
            self, 
            non_hours:list, 
            dynamic_caution_hours:dict, 
            prices:list, 
            prices_tomorrow:list,
            mock_hour: int|None = None
            ) -> None:
        hour = mock_hour or 21 #await self.parent.async_set_hour()
        ret_today, ret_tomorrow = await self.async_loop_nonhours(hour, non_hours, prices, prices_tomorrow)
        await self.async_loop_caution_hours(hour, dynamic_caution_hours, prices, prices_tomorrow, ret_today, ret_tomorrow)        
        await self.async_add_available_hours(hour, prices, prices_tomorrow, ret_today, ret_tomorrow)
        self.model.input_hours = await self.async_sort_dicts(ret_today, ret_tomorrow)        
        self.model.original_input_hours = self.model.input_hours.copy()

    @staticmethod
    async def async_add_available_hours(hour: int, prices:list, prices_tomorrow:list, ret_today: dict, ret_tomorrow:dict) -> None:
        _hour = hour
        _range = 24 if len(prices_tomorrow) > 0 else len(prices) < hour
        for i in range(_range):
            if _hour < hour and _hour not in ret_tomorrow.keys():
                ret_tomorrow[_hour] = (prices_tomorrow[_hour], 1)
                #todo: must test this without valid prices tomorrow.
            elif _hour >= hour and _hour not in ret_today.keys():
                ret_today[_hour] = (prices[_hour], 1)
            _hour += 1
            if _hour > 23:
                _hour = 0

    @staticmethod
    async def async_loop_caution_hours(hour: int, caution_hours:dict, prices:list, prices_tomorrow:list, ret_today: dict, ret_tomorrow: dict) -> None:
        for k, v in caution_hours.items():
            if k >= hour:
                ret_today[k] = (prices[k], v)
            else:
                ret_tomorrow[k] = (prices_tomorrow[k], v)

    @staticmethod
    async def async_loop_nonhours(hour: int, non_hours:list, prices:list, prices_tomorrow:list) -> Tuple[dict, dict]:
        ret_today = {}
        ret_tomorrow = {}
        for n in non_hours:
            if n >= hour:
                ret_today[n] = (prices[n], 0)
            else:
                ret_tomorrow[n] = (prices_tomorrow[n], 0)
        return ret_today, ret_tomorrow

    @staticmethod
    async def async_sort_dicts(ret_today: dict, ret_tomorrow:dict) -> dict:
        ret = {}
        for k in sorted(ret_today.keys()):
            ret[k] = ret_today[k]
        for k in sorted(ret_tomorrow.keys()):
            ret[k] = ret_tomorrow[k]
        return ret



