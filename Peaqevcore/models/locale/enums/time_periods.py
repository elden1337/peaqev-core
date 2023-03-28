from enum import Enum

class TimePeriods(Enum):
    QuarterHourly = "quarter-hourly"
    Hourly = "hourly"
    Daily = "daily"
    Weekly = "weekly"
    BiWeekly = "biweekly"
    Monthly = "monthly"
    Yearly = "yearly"
    UnSet = "unset"