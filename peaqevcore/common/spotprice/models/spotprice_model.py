import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

_LOGGER = logging.getLogger(__name__)


@dataclass
class SpotPriceModel:
    source: str
    currency: str = ""
    prices: list = field(default_factory=lambda: [])
    prices_tomorrow: list = field(default_factory=lambda: [])
    state: float = 0
    entity: str = ""
    _average_data: dict = field(default_factory=lambda: {})
    _average_stdev_data: dict = field(default_factory=lambda: {})
    average_month: float = 0
    adjusted_average: float = 0
    average_weekly: float = 0
    average_three_days: float = 0
    average_30: float = 0
    tomorrow_valid: bool = False
    daily_average: float = 0
    daily_average_date: date = None
    use_cent: bool = False
    dynamic_top_price_type: str = ""
    dynamic_top_price: float|None = None
    average_data_patched: bool = False

    @property
    def average_data(self) -> dict:
        return self._average_data
    
    @average_data.setter
    def average_data(self, value: dict|list) -> None:
        self._average_data = self.create_date_dict(value)

    @property
    def average_stdev_data(self) -> dict:
        return self._average_stdev_data
    
    @average_stdev_data.setter
    def average_stdev_data(self, value: dict|list) -> None:
        self._average_stdev_data = self.create_date_dict(value)

    def update_average_data(self, day : date = None, value: float = None) -> None:
        setdate = day if day else self.daily_average_date
        self._average_data[setdate] = value

    def update_average_stdev_data(self, day : date = None, value: float = None) -> None:
        setdate = day if day else self.daily_average_date
        self._average_stdev_data[setdate] = value

    def patch_average_data(self) -> None:
        """remove this 2024-05-01"""
        if self.average_data_patched:
            return
        patched_set = self.average_data.copy()
        for d in patched_set:
            if d + timedelta(days=1) in self.average_data:
                patched_set[d] = self.average_data[d + timedelta(days=1)]
        self.average_data = patched_set
        self.average_data_patched = True

    def create_date_dict(self, numbers: dict|list) -> dict:
        if isinstance(numbers, dict):
            try:
                ret = {datetime.strptime(key, "%Y-%m-%d").date(): value for key, value in numbers.items()}
            except ValueError:
                _LOGGER.error("Could not convert date string to date object")
                ret = {}
        else:
            today = date.today()
            delta = timedelta(days=len(numbers) - 1)
            start_date = today - delta
            ret = {}
            for number in numbers:
                ret[start_date] = number
                start_date += timedelta(days=1)
        return ret

    async def fix_dst(self, val) -> list | None:
        if val is None:
            return None
        if len(val) < 1:
            return []
        ll = [h for h in val if h is not None]
        av = round(min(ll), 3)
        if len(val) == 23:
            val.insert(2, av)
        elif val[2] is None:
            val[2] = av
        return val
