from dataclasses import dataclass, field
from datetime import date, datetime, time
from .hour_type import HourType
from .datetime_model import DateTimeModel


@dataclass
class HourPrice:
    idx: str = field(init=False)
    dt: datetime = field(init=False)
    day: date = date.today()
    hour: int = 0
    quarter: int = 0
    price: float = 0.0
    permittance: float = field(init=False)
    passed: bool = False
    hour_type: HourType = HourType.Regular

    def __post_init__(self):
        assert 0 <= self.quarter <= 3, "Quarter must be between 0 and 3"
        assert 0 <= self.hour <= 23, "Hour must be between 0 and 23"
        self.idx = f"{self.day}-{self.hour}-{self.quarter}"
        self.permittance = 1.0 if self.hour_type == HourType.BelowMin else 0.0
        self.dt = self._create_dt_object()

    def _create_dt_object(self) -> datetime:
        return datetime.combine(
            self.day,
            time(hour=self.hour, minute=self.quarter * 15, second=0, microsecond=0),
        )

    @staticmethod
    def set_hour_type(max_price, min_price, price):
        if price > max_price:
            return HourType.AboveMax
        elif price < min_price:
            return HourType.BelowMin
        return HourType.Regular

    def set_passed(self, dt: DateTimeModel):
        if dt.hdate > self.day:
            self.passed = True
        elif dt.hdate == self.day:
            if self.hour < dt.hour:
                self.passed = True
            elif self.hour == dt.hour and self.quarter < dt.quarter:
                print(f"{self.hour} {self.quarter} {dt.hour} {dt.quarter}")
                self.passed = True
        else:
            self.passed = False
