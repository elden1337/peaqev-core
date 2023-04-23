from ...models.locale.enums.calendar_periods import CalendarPeriods
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

TIMEPATTERN_FUNC = {
    CalendarPeriods.Hour: lambda a, dtp: dtp.hour in a,
    CalendarPeriods.Weekday: lambda a, dtp: dtp.weekday() in a,
    CalendarPeriods.Month: lambda a, dtp: dtp.month in a,
}


@dataclass
class TimePattern:
    pattern: List[Dict[CalendarPeriods, List[int]]]

    def valid(self, dt=datetime.now()) -> bool:
        total = []
        for p in self.pattern:
            total.append(all(TIMEPATTERN_FUNC[k](v, dt) for k, v in p.items()))
        return any(total)

    async def async_valid(self, dt=datetime.now()) -> bool:
        total = []
        for p in self.pattern:
            total.append(all(TIMEPATTERN_FUNC[k](v, dt) for k, v in p.items()))
        return any(total)
