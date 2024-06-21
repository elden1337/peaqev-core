from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from ...models.hourselection.hourselection_options import HourSelectionOptions


@dataclass
class ScheduleSession:
    hourselection_options: HourSelectionOptions | None
    remaining_charge: float = 0
    desired_charge: float = 0
    starttime: datetime = datetime.min
    departuretime: datetime = datetime.min
    _hours_price: dict[datetime, float] = field(init=False)
    _hours_charge: dict[datetime, float] = field(init=False)
    _nh: list = field(default_factory=lambda: [])
    _ch: dict = field(default_factory=lambda: {})
    _mock_dt: datetime | None = None
    _init_ok: bool = False
    override_settings: bool = False
    _tomorrow_valid: bool = False

    def update_remaining_charge(self, charged_amount: float):
        rem = max(self.desired_charge - charged_amount,0)
        self.remaining_charge = round(rem, 2)

    @property
    def hours_price(self):
        return self._hours_price

    @hours_price.setter
    def hours_price(self, prices: list):
        today_date = datetime.now() if self._mock_dt is None else self._mock_dt
        price_dict = {}
        for idx, price in enumerate(prices[0]):
            price_dict[datetime.combine(today_date.date(), time(idx, 0))] = price
        if prices[1] is not None:
            self._tomorrow_valid = True
            tomorrow_date = today_date.date() + timedelta(days=1)
            for idx, price in enumerate(prices[1]):
                price_dict[datetime.combine(tomorrow_date, time(idx, 0))] = price
        else:
            self._tomorrow_valid = False
        self._hours_price = self._filter_price_dict(
            price_dict, self.starttime, self.departuretime
        )

    @property
    def hours_charge(self) -> dict:
        if self._init_ok:
            return self._hours_charge
        return dict()

    @hours_charge.setter
    def hours_charge(self, val):
        self._hours_charge = val
        self._init_ok = True

    @property
    def non_hours(self) -> list[datetime]:
        self._make_hours()
        return self._nh

    @property
    def caution_hours(self) -> dict[datetime, float]:
        self._make_hours()
        return self._ch

    def _make_hours(self) -> None:
        ch = {}
        nh = []
        _timer = datetime.combine(self.starttime.date(), time(self.starttime.hour, 0))
        today_dt = datetime.now() if self._mock_dt is None else self._mock_dt
        today_dt = today_dt.replace(minute=0, second=0, microsecond=0)  # start of the current hour
        while _timer < self.departuretime:
            if _timer >= today_dt:
                if _timer not in self.hours_charge.keys():
                    if self._tomorrow_valid or _timer.hour > today_dt.hour:
                        nh.append(_timer)
                elif 0 < self.hours_charge[_timer] < 1:
                    if self._tomorrow_valid or _timer.hour > today_dt.hour:
                        ch[_timer] = self.hours_charge[_timer]
            _timer += timedelta(hours=1)
        self._nh = nh
        self._ch = ch

    def _filter_price_dict(self, price_dict: dict, starttime: datetime, departuretime: datetime) -> dict:
        starttime_hour = datetime(starttime.year, starttime.month, starttime.day, starttime.hour)
        ret = {
            key: value
            for (key, value) in price_dict.items()
            if starttime_hour <= key <= departuretime
        }
        return ret