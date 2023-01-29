from enum import Enum

class TimePeriods(Enum):
    QuarterHourly = "quarterhourly"
    Hourly = "hourly"
    Daily = "daily"
    Weekly = "weekly"
    BiWeekly = "biweekly"
    Monthly = "monthly"
    Yearly = "yearly"
    UnSet = "unset"