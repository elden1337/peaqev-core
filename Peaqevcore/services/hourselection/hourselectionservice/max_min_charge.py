from dataclasses import dataclass, field
from typing import Tuple
import asyncio

@dataclass
class hoursexportmodel:
    input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    original_input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    avg24: float|None = None

    @property
    def total_charge(self) -> float:
        return self._total_charge
    
    @total_charge.setter
    def total_charge(self, value: float) -> None:
        self._total_charge = round(value,1)

    async def async_update(self, avg24, peak, max_desired) -> None:
        if round(avg24,1) != self.avg24:
            self.avg24 = round(avg24,1)
        for i in range(len(self.original_input_hours.items())):
            _sum = await self.async_sum_charge(peak)
            if _sum > max_desired:
                await self.async_decrease()
            elif _sum < max_desired:
                await self.async_increase()
        self.total_charge = await self.async_sum_charge(peak)

    async def async_sum_charge(self, peak) -> float:
        total=0
        for k, v in self.input_hours.items():
            total += (peak-self.avg24)*v[1]
        return total

    async def async_decrease(self):
        max_key = max(
            self.input_hours, 
            key=lambda k: self.input_hours[k][0] if self.input_hours[k][1] != 0 else -1
            )
        self.input_hours[max_key] = (self.input_hours[max_key][0], 0)

    async def async_increase(self):
        min_key = min(
            self.input_hours, 
            key=lambda k: self.input_hours[k][0] if self.input_hours[k][1] < 1 else 999
            )
        self.input_hours[min_key] = (self.input_hours[min_key][0], min(
            1, 
            self.original_input_hours[min_key][1]
            ))

    async def async_make_hours(self, non_hours:list, dynamic_caution_hours:dict, prices:list, prices_tomorrow:list) -> None:
        ret_today = {}
        ret_tomorrow = {}
        hour = 21 #await self.parent.async_set_hour()
        for n in non_hours:
            if n >= hour:
                ret_today[n] = (prices[n], 0)
            else:
                ret_tomorrow[n] = (prices_tomorrow[n], 0)
        for k, v in dynamic_caution_hours.items():
            if k >= hour:
                ret_today[k] = (prices[k], v)
            else:
                ret_tomorrow[k] = (prices_tomorrow[k], v)
        _hour = hour
        for i in range(24):
            if _hour < hour and _hour not in ret_tomorrow.keys():
                ret_tomorrow[_hour] = (prices_tomorrow[_hour], 1)
                #todo: must test this without valid prices tomorrow.
            elif _hour >= hour and _hour not in ret_today.keys():
                ret_today[_hour] = (prices[_hour], 1)
            _hour += 1
            if _hour > 23:
                _hour = 0
        ret = {}
        for k in sorted(ret_today.keys()):
            ret[k] = ret_today[k]
        for k in sorted(ret_tomorrow.keys()):
            ret[k] = ret_tomorrow[k]
        
        self.input_hours = ret
        self.original_input_hours = self.input_hours.copy()


async def do():
    avg = 0.69
    peak = 2.28
    max_desired = 8
    non_hours = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 21]
    prices = [0.54, 0.55, 0.57, 0.6, 0.62, 0.72, 0.74, 0.88, 0.9, 0.83, 0.77, 0.81, 0.77, 0.72, 0.61, 0.55, 0.51, 0.56, 0.58, 0.52, 0.44, 0.42, 0.34, 0.15]
    prices_tomorrow = [0.07, 0.07, 0.06, 0.06, 0.06, 0.11, 0.41, 0.45, 0.47, 0.45, 0.44, 0.42, 0.4, 0.4, 0.35, 0.37, 0.39, 0.41, 0.41, 0.41, 0.39, 0.35, 0.29, 0.21]

    dynamic_caution_hours = {}
    h = hoursexportmodel()
    await h.async_make_hours(non_hours, dynamic_caution_hours, prices, prices_tomorrow)
    print(h.input_hours)

    await h.async_update(avg, peak, max_desired)
    print(f"desired is {max_desired}")
    print(h.total_charge)
    print(f"orig non_hours: {[k for k, v in h.original_input_hours.items() if v[1] == 0]}")
    print(f"non_hours: {[k for k, v in h.input_hours.items() if v[1] == 0]}")
    # print("---")
    # print(f"orig full hours: {[k for k, v in h.original_input_hours.items() if v[1] == 1]}")
    # print(f"full hours: {[k for k, v in h.input_hours.items() if v[1] == 1]}")
    # print("---")
    # print(f"orig caution hours: {[k for k, v in h.original_input_hours.items() if 0 < v[1] < 1]}")
    # print(f"caution hours: {[k for k, v in h.input_hours.items() if 0 < v[1] < 1]}")
    # print("#---")
    # await h.async_update(avg, peak, max_desired*5)
    # print(f"desired is {max_desired*5}")
    # print(h.total_charge)
    # print(f"orig non_hours: {[k for k, v in h.original_input_hours.items() if v[1] == 0]}")
    # print(f"non_hours: {[k for k, v in h.input_hours.items() if v[1] == 0]}")
    # print("---")
    # print(f"orig full hours: {[k for k, v in h.original_input_hours.items() if v[1] == 1]}")
    # print(f"full hours: {[k for k, v in h.input_hours.items() if v[1] == 1]}")
    # print("---")
    # print(f"orig caution hours: {[k for k, v in h.original_input_hours.items() if 0 < v[1] < 1]}")
    # print(f"caution hours: {[k for k, v in h.input_hours.items() if 0 < v[1] < 1]}")
    
asyncio.run(do())



