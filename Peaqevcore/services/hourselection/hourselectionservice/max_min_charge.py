from dataclasses import dataclass, field
from typing import Tuple
import asyncio

@dataclass
class hoursexportmodel:
    input_hours: dict[int, Tuple[float, float]]
    original_input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    
    def __post_init__(self) -> None:
        self.original_input_hours = self.input_hours.copy()

    @property
    def total_charge(self) -> float:
        return self._total_charge
    
    @total_charge.setter
    def total_charge(self, value: float) -> None:
        self._total_charge = round(value,1)

    async def async_update(self, avg24, peak, max_desired) -> None:
        for i in range(0,25):
            if await self.async_sum_charge(avg24, peak) > max_desired:
                await self.async_decrease()
        for i in range(0,25):
            if await self.async_sum_charge(avg24, peak) < max_desired:
                await self.async_increase()
        self.total_charge = await self.async_sum_charge(avg24, peak)

    async def async_sum_charge(self, avg24, peak) -> float:
        total=0
        for k, v in self.input_hours.items():
            total += (peak-avg24)*v[1]
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
        self.input_hours[min_key] = (self.input_hours[min_key][0], min(1, self.original_input_hours[min_key][1]))


async def do():
    avg = 0.69
    peak = 2.28
    max_desired = 8
    available_hours = {
        0: (0.07,1), 1: (0.07,1), 2: (0.06,1), 3: (0.06,1), 4: (0.14,1), 6: (0.61,1), 
        7: (0.72,0), 8: (0.83,0), 9: (0.81,0), 10: (0.62,1), 11: (0.51,1), 12: (0.49,1), 
        13: (0.47,1), 14: (0.42,1), 15: (0.45,1), 16: (0.56,1), 17: (0.74,1), 18: (0.69,1), 19: (0.63,1), 20: (0.54,1), 5: (0.53, 0.8), 21: (0.6, 0.7), 22: (0.55, 0.77), 23: (0.51, 0.82)}
    
    h = hoursexportmodel(input_hours=available_hours)
    print(f"original: {await h.async_sum_charge(avg, peak)}")
    await h.async_update(avg, peak, max_desired)
    print(f"desired is {max_desired}")
    print(h.total_charge)
    print(f"orig non_hours: {[k for k, v in h.original_input_hours.items() if v[1] == 0]}")
    print(f"non_hours: {[k for k, v in h.input_hours.items() if v[1] == 0]}")
    print("---")
    print(f"orig full hours: {[k for k, v in h.original_input_hours.items() if v[1] == 1]}")
    print(f"full hours: {[k for k, v in h.input_hours.items() if v[1] == 1]}")
    print("---")
    print(f"orig caution hours: {[k for k, v in h.original_input_hours.items() if 0 < v[1] < 1]}")
    print(f"caution hours: {[k for k, v in h.input_hours.items() if 0 < v[1] < 1]}")
    print("#---")
    await h.async_update(avg, peak, max_desired*5)
    print(f"desired is {max_desired*5}")
    print(h.total_charge)
    print(f"orig non_hours: {[k for k, v in h.original_input_hours.items() if v[1] == 0]}")
    print(f"non_hours: {[k for k, v in h.input_hours.items() if v[1] == 0]}")
    print("---")
    print(f"orig full hours: {[k for k, v in h.original_input_hours.items() if v[1] == 1]}")
    print(f"full hours: {[k for k, v in h.input_hours.items() if v[1] == 1]}")
    print("---")
    print(f"orig caution hours: {[k for k, v in h.original_input_hours.items() if 0 < v[1] < 1]}")
    print(f"caution hours: {[k for k, v in h.input_hours.items() if 0 < v[1] < 1]}")
    # await h.async_update(avg, peak, 12)
    # print("desired is 12")
    # print(h.non_hours)
    # print(h.available_hours)
    # print(h.caution_hours)
    # print(h.total_charge)
    # await h.async_update(avg, peak, 32)
    # print("desired is 32")
    # print(h.non_hours)
    # print(h.available_hours)
    # print(h.caution_hours)
    # print(h.total_charge)

asyncio.run(do())



