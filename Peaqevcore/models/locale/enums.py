from enum import Enum

class Dividents(Enum):
    AND = 1
    OR = 2
    UNSET = 3

class SumTypes(Enum):
    Max = 1
    Avg = 2
    Min = 3

class TimePeriods(Enum):
    Hourly = 1
    Daily = 2
    Weekly = 3
    BiWeekly = 4
    Monthly = 5
    Yearly = 6
    UnSet = 7

class CalendarPeriods(Enum):
    Minute = 1
    Hour = 2
    Weekday = 3
    Month = 4
    Quarter = 5

class PriceType(Enum):
    Static = 0
    Tiered = 1


