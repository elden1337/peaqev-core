# from dataclasses import dataclass, field
# from typing import Tuple
# import asyncio

# @dataclass
# class hoursexportmodel:
#     non_hours: list[int] = field(default_factory=lambda: [])
#     caution_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
#     available_hours: dict[int, float] = field(default_factory=lambda: {})
#     _total_charge: float = 0

#     original_non_hours: list[int] = field(default_factory=lambda: [])
#     original_caution_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
#     original_available_hours: dict[int, float] = field(default_factory=lambda: {})
                
#     def __post_init__(self) -> None:
#         self.original_non_hours = self.non_hours.copy()
#         self.original_caution_hours = self.caution_hours.copy()
#         self.original_available_hours = self.available_hours.copy()
#         self.available_hours = dict(sorted(self.available_hours.items()))

#     @property
#     def total_charge(self) -> float:
#         return self._total_charge
    
#     @total_charge.setter
#     def total_charge(self, value: float) -> None:
#         self._total_charge = round(value,1)

#     async def async_update(self, avg24, peak, max_desired) -> None:
#         while await self.async_sum_charge(avg24, peak) > max_desired:
#             await self.async_decrease()        
#         while await self.async_sum_charge(avg24, peak) < max_desired and len(self.original_non_hours) != len(self.non_hours):
#             await self.async_increase()
#         self.total_charge = await self.async_sum_charge(avg24, peak)

#     async def async_sum_charge(self, avg24, peak) -> float:
#         total=0
#         for k, v in self.available_hours.items():
#             if all([
#                 k not in self.non_hours,
#                 k not in self.caution_hours.keys()
#                 ]):
#                 total += peak-avg24
#         for k, v in self.caution_hours.items():
#             if k not in self.non_hours:
#                 total += (peak-avg24)*v[1]
#         return total

#     async def async_decrease(self):
#         max_key = max(self.available_hours, key=self.available_hours.get)
#         self.available_hours.pop(max_key)
#         if max_key not in self.non_hours:
#             self.non_hours.append(max_key)
#         self.available_hours = dict(sorted(self.available_hours.items()))
#         self.non_hours = list(sorted(self.non_hours))

#     async def async_increase(self):
#         """get the lowest value from original available hours which is not in original non hours and add it to available hours. remove it from non hours. sort available hours"""
#         availables = {k: v for k, v in self.original_available_hours.items() if k not in self.available_hours}
#         min_key = min(availables, key=availables.get)
#         self.available_hours[min_key] = availables[min_key]
#         self.non_hours.remove(min_key)
#         self.available_hours = dict(sorted(self.available_hours.items()))


# async def do():
#     avg = 0.69
#     peak = 2.28
#     max_desired = 8
#     available_hours = {0: 0.07, 1: 0.07, 2: 0.06, 3: 0.06, 4: 0.14, 6: 0.61, 7: 0.72, 8: 0.83, 9: 0.81, 10: 0.62, 11: 0.51, 12: 0.49, 13: 0.47, 14: 0.42, 15: 0.45, 16: 0.56, 17: 0.74, 18: 0.69, 19: 0.63, 20: 0.54}
#     non_hours = [6,7,8,9,10,11,16,17,18,19,20]
#     caution_hours = {5: (0.53, 0.8), 21: (0.6, 0.7), 22: (0.55, 0.77), 23: (0.51, 0.82)}
#     h = hoursexportmodel(available_hours=available_hours, non_hours=non_hours, caution_hours=caution_hours)
#     print(f"original: {await h.async_sum_charge(avg, peak)}")
#     await h.async_update(avg, peak, max_desired)
#     print("desired is 8")
#     print(h.non_hours)
#     print(h.available_hours)
#     print(h.caution_hours)
#     print(h.total_charge)
#     await h.async_update(avg, peak, 12)
#     print("desired is 12")
#     print(h.non_hours)
#     print(h.available_hours)
#     print(h.caution_hours)
#     print(h.total_charge)
#     await h.async_update(avg, peak, 32)
#     print("desired is 32")
#     print(h.non_hours)
#     print(h.available_hours)
#     print(h.caution_hours)
#     print(h.total_charge)

# asyncio.run(do())

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
        while await self.async_sum_charge(avg24, peak) > max_desired:
            await self.async_decrease()        
        while await self.async_sum_charge(avg24, peak) < max_desired:
            await self.async_increase()
        self.total_charge = await self.async_sum_charge(avg24, peak)

    async def async_sum_charge(self, avg24, peak) -> float:
        total=0
        for k, v in self.input_hours.items():
            total += (peak-avg24)*v[1]
        return total

    async def async_decrease(self):
        max_key = max(self.available_hours, key=self.available_hours.get)
        self.available_hours.pop(max_key)
        if max_key not in self.non_hours:
            self.non_hours.append(max_key)
        self.available_hours = dict(sorted(self.available_hours.items()))
        self.non_hours = list(sorted(self.non_hours))

    async def async_increase(self):
        """get the lowest value from original available hours which is not in original non hours and add it to available hours. remove it from non hours. sort available hours"""
        availables = {k: v for k, v in self.original_available_hours.items() if k not in self.available_hours}
        min_key = min(availables, key=availables.get)
        self.available_hours[min_key] = availables[min_key]
        self.non_hours.remove(min_key)
        self.available_hours = dict(sorted(self.available_hours.items()))


async def do():
    avg = 0.69
    peak = 2.28
    max_desired = 8
    available_hours = {
        0: (0.07,1), 1: (0.07,1), 2: (0.06,1), 3: (0.06,1), 4: (0.14,1), 6: (0.61,1), 
        7: (0.72,1), 8: (0.83,1), 9: (0.81,1), 10: (0.62,1), 11: (0.51,1), 12: (0.49,1), 
        13: (0.47,1), 14: (0.42,1), 15: (0.45,1), 16: (0.56,1), 17: (0.74,1), 18: (0.69,1), 19: (0.63,1), 20: (0.54,1), 5: (0.53, 0.8), 21: (0.6, 0.7), 22: (0.55, 0.77), 23: (0.51, 0.82)}
    
    h = hoursexportmodel(input_hours=available_hours)
    print(f"original: {await h.async_sum_charge(avg, peak)}")
    # await h.async_update(avg, peak, max_desired)
    # print("desired is 8")
    # print(h.non_hours)
    # print(h.available_hours)
    # print(h.caution_hours)
    # print(h.total_charge)
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



