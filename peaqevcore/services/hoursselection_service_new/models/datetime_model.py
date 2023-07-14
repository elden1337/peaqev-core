from dataclasses import dataclass, field
from datetime import datetime, date, timedelta


@dataclass
class DateTimeModel:
    _datetime: datetime = field(default_factory=datetime.now)
    _datetime_set: bool = False
    _date: date = field(default_factory=date.today)
    _date_set: bool = False
    _hour: int = 0
    _hour_set: bool = False
    _quarter: int = 0
    _quarter_set: bool = False

    def set_datetime(self, mock_dt: datetime):
        assert isinstance(mock_dt, datetime), "Datetime must be a datetime object"
        self._datetime = mock_dt.replace(minute=0, second=0, microsecond=0)
        self._datetime_set = True
        self._date = mock_dt.date()
        self._date_set = True
        self._hour = mock_dt.hour
        self._hour_set = True
        self._quarter = mock_dt.minute // 15
        self._quarter_set = True

    def set_date(self, mock_date: date):
        assert isinstance(mock_date, date), "Date must be a date object"
        self._date = mock_date
        self._date_set = True

    def set_hour(self, mock_hour: int):
        assert 0 <= mock_hour <= 23, "Hour must be between 0 and 23"
        self._hour = mock_hour
        self._hour_set = True

    def set_quarter(self, mock_quarter: int):
        assert 0 <= mock_quarter <= 3, "Quarter must be between 0 and 3"
        self._quarter = mock_quarter
        self._quarter_set = True

    def is_passed(self, datum, hour, quarter) -> bool:
        if datum == self.hdate_tomorrow:
            return False
        if self.hour > hour:
            return True
        elif self.hour == hour:
            if self.quarter > quarter:
                return True
        return False

    @property
    def dt(self) -> datetime:
        return (
            self._datetime
            if self._datetime_set
            else datetime.now().replace(minute=0, second=0, microsecond=0)
        )

    @property
    def hdate(self) -> date:
        return self._date if self._date_set else date.today()

    @property
    def hdate_tomorrow(self) -> date:
        return self.hdate + timedelta(days=1)

    @property
    def hour(self) -> int:
        return self._hour if self._hour_set else datetime.now().hour

    @property
    def quarter(self) -> int:
        return self._quarter if self._quarter_set else (datetime.now().minute // 15)
