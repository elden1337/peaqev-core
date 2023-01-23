from ...models.locale.enums.calendar_periods import CalendarPeriods
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

FREECHARGE_FUNC = {
    CalendarPeriods.Hour: lambda a, dtp: dtp.hour in a,
    CalendarPeriods.Weekday: lambda a, dtp: dtp.weekday() in a,
    CalendarPeriods.Month: lambda a, dtp: dtp.month in a,
}

@dataclass
class FreeChargePattern:
    pattern: List[Dict[CalendarPeriods,List[int]]]

    def free_charge(self, dt = datetime.now()) -> bool:
        total = []
        for p in self.pattern:
            total.append(all(FREECHARGE_FUNC[k](v, dt) for k, v in p.items()))
        return any(total)

