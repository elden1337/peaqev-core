from .querytypes.models.enums import CalendarPeriods
from typing import List
from dataclasses import dataclass
from datetime import datetime, date, time

FREECHARGE_FUNC = {
    CalendarPeriods.Hour: lambda a, dtp: dtp.hour in a,
    CalendarPeriods.Weekday: lambda a, dtp: dtp.weekday() in a,
    CalendarPeriods.Month: lambda a, dtp: dtp.month in a,
}

@dataclass
class FreeChargePattern:
    pattern: List[dict[CalendarPeriods,List[int]]]

    def free_charge(self, dt = datetime.now()) -> bool:
        total = []
        for p in self.pattern:
            total.append(all(FREECHARGE_FUNC[k](v, dt) for k, v in p.items()))
        return any(total)
    

# free_new = FreeChargePattern([
#     {
#         CalendarPeriods.Month: [1,2,3,4,5,6,7,8,9,10,11,12],
#         CalendarPeriods.Weekday: [0, 1, 2, 3, 4],
#         CalendarPeriods.Hour: [19,20,21,22, 23, 0, 1, 2, 3, 4, 5,6]
#     },
#     {
#         CalendarPeriods.Month: [1,2,3,4,5,6,7,8,9,10,11,12],
#         CalendarPeriods.Weekday: [5,6],
#         CalendarPeriods.Hour: [0, 1, 2, 3, 4, 5, 6,7,8,9,10,11,12,13,14,15,16,17,18,19, 20, 21, 22, 23]
#     }
# ])


# _dt = datetime.combine(date(2022, 6, 27), time(10, 30))
# print(free_new.free_charge(dt=_dt))
