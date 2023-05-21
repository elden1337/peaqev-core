# from .models.datetime_model import DateTimeModel
# from .models.hour_price import HourPrice
# from .models.hourselection_model import HourSelectionModel


# -----------------hour_type.py
from enum import Enum


class HourType(Enum):
    Regular = 0
    AboveMax = 1
    BelowMin = 2


# -----------------datetime_model.py
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta


@dataclass
class DateTimeModel:
    _date: date = field(default_factory=date.today)
    _date_set: bool = False
    _hour: int = 0
    _hour_set: bool = False
    _quarter: int = 1
    _quarter_set: bool = False

    async def async_set_date(self, mock_date: date):
        assert isinstance(mock_date, date), "Date must be a date object"
        self._date = mock_date
        self._date_set = True

    async def async_set_hour(self, mock_hour: int):
        assert 0 <= mock_hour <= 23, "Hour must be between 0 and 23"
        self._hour = mock_hour
        self._hour_set = True

    async def async_set_quarter(self, mock_quarter: int):
        assert 1 <= mock_quarter <= 4, "Quarter must be between 0 and 3"
        self._quarter = mock_quarter
        self._quarter_set = True

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
        return self._quarter if self._quarter_set else (datetime.now().minute // 15) + 1


# -----------------hourprice.py
from dataclasses import dataclass, field
from datetime import date


@dataclass
class HourPrice:
    idx: str = field(init=False)
    day: date = date.today()
    hour: int = 0
    quarter: int = 1
    price: float = 0.0
    permittance: float = field(init=False)
    passed: bool = False
    hour_type: HourType = HourType.Regular

    def __post_init__(self):
        assert 1 <= self.quarter <= 4, "Quarter must be between 0 and 3"
        assert 0 <= self.hour <= 23, "Hour must be between 0 and 23"
        self.idx = f"{self.day}-{self.hour}-{self.quarter}"
        self.permittance = 1.0 if self.hour_type == HourType.BelowMin else 0.0

    @staticmethod
    async def async_set_hour_type(max_price, min_price, price):
        if price > max_price:
            return HourType.AboveMax
        elif price < min_price:
            return HourType.BelowMin
        return HourType.Regular

    async def async_set_passed(self, dt: DateTimeModel):
        if dt.hdate > self.day:
            self.passed = True
        elif dt.hdate == self.day:
            if self.hour < dt.hour:
                self.passed = True
            elif self.hour == dt.hour and self.quarter < dt.quarter:
                self.passed = True
        else:
            self.passed = False


# -----------------hourselection_model.py
from dataclasses import dataclass, field


@dataclass
class HourSelectionModel:
    prices_today: list[float] = field(default_factory=list)
    prices_tomorrow: list[float] = field(default_factory=list)
    hours_prices: list[HourPrice] = field(default_factory=list)


# -----------------hourselection_options.py
from dataclasses import dataclass, field


@dataclass
class HourSelectionOptions:
    caution_hour_type: str = "regular"
    max_price: float = float("inf")
    min_price: float = 0.0


# -----------------
class HourSelectionService:
    def __init__(self, options: HourSelectionOptions = HourSelectionOptions()):
        self.options = options
        self.model = HourSelectionModel()
        self.dtmodel = DateTimeModel()

    async def async_update(self):
        print(self.dtmodel)
        for hp in self.model.hours_prices:
            await hp.async_set_passed(self.dtmodel)

    async def async_update_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ):
        self.model.prices_today = prices  # clean first
        self.model.prices_tomorrow = prices_tomorrow  # clean first
        self.model.hours_prices = await self.async_create_hour_prices(
            prices, prices_tomorrow
        )

    async def async_create_hour_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        match len(prices):
            case 24:
                return await self.async_create_hour_prices_hourly(
                    prices, prices_tomorrow
                )
            case 96:
                return await self.async_create_hour_prices_quarterly(
                    prices, prices_tomorrow
                )
        raise ValueError("Prices must be either 24 or 96")

    async def async_create_hour_prices_quarterly(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        return []

    async def async_create_hour_prices_hourly(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        ret = []
        for idx, p in enumerate(prices):
            assert isinstance(p, float)
            ret.append(
                HourPrice(
                    day=self.dtmodel.hdate,
                    hour=idx,
                    price=p,
                    passed=True if idx < self.dtmodel.hour else False,
                    hour_type=await HourPrice.async_set_hour_type(
                        self.options.max_price, self.options.min_price, p
                    ),
                )
            )
        for idx, p in enumerate(prices_tomorrow):
            assert isinstance(p, float)
            ret.append(
                HourPrice(
                    day=self.dtmodel.hdate_tomorrow,
                    hour=idx,
                    price=p,
                    passed=False,
                    hour_type=await HourPrice.async_set_hour_type(
                        self.options.max_price, self.options.min_price, p
                    ),
                )
            )
        return ret


import asyncio

P230520 = [
    [
        0.22,
        0.17,
        0.15,
        0.16,
        0.1,
        0.1,
        0.11,
        0.14,
        0.15,
        0.15,
        0.14,
        0.08,
        0.08,
        0.07,
        0.08,
        0.08,
        0.1,
        0.17,
        0.65,
        0.74,
        0.62,
        0.17,
        0.11,
        0.09,
    ],
    [
        0.08,
        0.08,
        0.08,
        0.08,
        0.08,
        0.08,
        0.1,
        0.12,
        0.13,
        0.11,
        0.08,
        0.07,
        0.02,
        0.01,
        0.02,
        0.03,
        0.07,
        0.11,
        0.67,
        1.07,
        1.15,
        1.08,
        0.64,
        0.13,
    ],
]


async def do():
    opt = HourSelectionOptions(max_price=2, min_price=0.05)
    hss = HourSelectionService(opt)
    await hss.async_update_prices(P230520[0], P230520[1])
    # for p in hss.model.hours_prices:
    #     print(p)

    print("---- updating date")
    await hss.dtmodel.async_set_date(date(2023, 5, 24))
    await hss.async_update()
    for p in hss.model.hours_prices:
        print(p)

    # print(list(map(lambda x: x.quarter, hss.model.hours_prices)))
    # filtered_list = list(
    #     filter(lambda obj: obj.hour_type == HourType.BelowMin, hss.model.hours_prices)
    # )
    # for f in filtered_list:
    #     print(f)


if __name__ == "__main__":
    asyncio.run(do())
