from enum import Enum

class TimePeriods(Enum):
    QuarterHourly = 0
    Hourly = 1
    Daily = 2
    Weekly = 3
    BiWeekly = 4
    Monthly = 5
    Yearly = 6
    UnSet = 7