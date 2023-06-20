from .models.stop_string import AllowanceObj, set_allowance_obj
from .models.datetime_model import DateTimeModel
from .models.hour_price import HourPrice
from .models.hourselection_model import HourSelectionModel
from statistics import stdev, mean, variance
from datetime import date, datetime, timedelta
from ...models.hourselection.hourselection_options import HourSelectionOptions
from .const import TODAY, TOMORROW
from .hourselection_calculations import (
    normalize_prices,
    deviation_from_mean,
)
from .permittance import set_initial_permittance, set_scooped_permittance
from .max_min_charge import MaxMinCharge


class HourSelectionService:
    def __init__(self, options: HourSelectionOptions = HourSelectionOptions()):
        self.options = options
        self.dtmodel = DateTimeModel()
        self.model = HourSelectionModel()
        self.max_min = MaxMinCharge(service=self, min_price=self.options.min_price)
        self._offset_dict: dict[datetime, dict] = {}

    def update(self):
        for hp in self.model.hours_prices:
            hp.set_passed(self.dtmodel)

    async def async_update(self):
        self.update()

    @property
    def all_hours(self) -> list[HourPrice]:
        self.update()
        return self.model.hours_prices

    @property
    def future_hours(self) -> list[HourPrice]:
        self.update()
        ret = [hp for hp in self.model.hours_prices if not hp.passed]
        if self.max_min.active:
            for r in ret:
                r.permittance = 0.0 if r.dt in self.max_min.non_hours else 1.0
        return ret

    @property
    def passed_hours(self) -> list[HourPrice]:
        self.update()
        return [hp for hp in self.model.hours_prices if hp.passed]

    @property
    def stopped_string(self) -> str:
        return self.allowance.display_name

    @property
    def allowance(self) -> AllowanceObj:
        return set_allowance_obj(self.dtmodel, self.future_hours)

    @property
    def average_kwh_price(self) -> float:
        return round(mean([hp.permittance * hp.price for hp in self.future_hours]), 2)

    @property
    def non_hours(self) -> list[datetime]:
        return [
            hp.dt
            for hp in self.model.hours_prices
            if not hp.passed and hp.permittance == 0.0
        ]

    @property
    def caution_hours(self) -> list[datetime]:
        return list(self.dynamic_caution_hours.keys())

    @property
    def dynamic_caution_hours(self) -> dict[datetime, float]:
        return {
            hp.dt: hp.permittance
            for hp in self.model.hours_prices
            if not hp.passed and 0.0 < hp.permittance < 1.0
        }

    @property
    def offset_dict(self) -> dict:
        return self._get_offset_dict()

    async def async_update_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ):
        self.model.prices_today = prices  # clean first
        self.model.prices_tomorrow = prices_tomorrow  # clean first
        if self._do_recalculate_prices(prices):
            self.model.hours_prices = await self.async_create_prices(
                prices, prices_tomorrow
            )

    async def async_update_adjusted_average(self, adjusted_average: float) -> None:
        self.model.adjusted_average = adjusted_average
        self.update()
        if len(self.model.hours_prices) > 0:
            await self.async_set_permittance(self.model.hours_prices)

    def _do_recalculate_prices(self, prices) -> bool:
        if [
            hp.price for hp in self.model.hours_prices if hp.day == self.dtmodel.hdate
        ] == prices:
            return False
        return True

    async def async_create_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        # todo: fix to allow 23, 24,25, 92, 96, 100 for dst-dates.
        match len(prices):
            case 23 | 24 | 25:
                return await self.async_create_hour_prices_hourly(
                    prices, prices_tomorrow
                )
            case 92 | 96 | 100:
                return await self.async_create_hour_prices_quarterly(
                    prices, prices_tomorrow
                )
            case 0:
                return []
        raise ValueError(
            f"Length of pricelist must be either 23,24,25,92,96 or 100. Your length is {len(prices)}"
        )

    def _is_passed(self, hour, quarter) -> bool:
        if self.dtmodel.hour > hour:
            return True
        elif self.dtmodel.hour == hour:
            if self.dtmodel.quarter >= quarter:
                return True
        return False

    async def async_create_hour_prices_quarterly(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        # todo: handle here first if prices or prices_tomorrow are 92 or 100 in length (dst shift)
        ret = []
        for idx, p in enumerate(prices):
            assert isinstance(p, (float, int))
            hour = int(idx / 4)
            quarter = idx % 4
            ret.append(
                HourPrice(
                    day=self.dtmodel.hdate,
                    hour=hour,
                    quarter=quarter,
                    price=p,
                    passed=self._is_passed(hour, quarter),
                    hour_type=HourPrice.set_hour_type(
                        self.options.absolute_top_price, self.options.min_price, p
                    ),
                )
            )
        for idx, p in enumerate(prices_tomorrow):
            assert isinstance(p, (float, int))
            hour = int(idx / 4)
            quarter = idx % 4
            ret.append(
                HourPrice(
                    day=self.dtmodel.hdate_tomorrow,
                    hour=hour,
                    quarter=quarter,
                    price=p,
                    passed=False,
                    hour_type=HourPrice.set_hour_type(
                        self.options.absolute_top_price, self.options.min_price, p
                    ),
                )
            )
        await self.async_set_permittance(ret)
        return ret

    async def async_create_hour_prices_hourly(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> list:
        ret = []
        # todo: handle here first if prices or prices_tomorrow are 23 or 25 in length (dst shift)
        for idx, p in enumerate(prices):
            assert isinstance(p, (float, int))
            ret.append(
                HourPrice(
                    day=self.dtmodel.hdate,
                    hour=idx,
                    price=p,
                    passed=True if idx < self.dtmodel.hour else False,
                    hour_type=HourPrice.set_hour_type(
                        self.options.absolute_top_price, self.options.min_price, p
                    ),
                )
            )
        for idx, p in enumerate(prices_tomorrow):
            assert isinstance(p, (float, int))
            ret.append(
                HourPrice(
                    day=self.dtmodel.hdate_tomorrow,
                    hour=idx,
                    price=p,
                    passed=False,
                    hour_type=HourPrice.set_hour_type(
                        self.options.absolute_top_price, self.options.min_price, p
                    ),
                )
            )
        await self.async_set_permittance(ret)
        return ret

    async def async_set_permittance(self, hour_prices: list[HourPrice]) -> None:
        prices = normalize_prices([hp.price for hp in hour_prices])
        set_initial_permittance(
            hour_prices,
            self._set_price_mean(prices, self.model.adjusted_average),
            stdev(prices),
        )
        set_scooped_permittance(hour_prices, self.options.cautionhour_type_enum)
        self._offset_dict = self._set_offset_dict(prices, hour_prices[0].day)

    def _get_offset_dict(self) -> dict:
        vals = self._offset_dict.keys()
        if len(vals) == 1:
            return {TODAY: self._offset_dict.values(), TOMORROW: {}}
        elif len(vals) == 2:
            return {
                TODAY: self._offset_dict[min(vals)],
                TOMORROW: self._offset_dict[max(vals)],
            }
        # todo: log something here.
        return {
            TODAY: {},
            TOMORROW: {},
        }

    @staticmethod
    def _set_offset_dict(prices: list[float], day: date) -> dict:
        ret = {}
        _len = len(prices)
        today: list = []
        tomorrow: list = []
        match _len:
            case 23 | 24 | 25 | 92 | 96 | 100:
                today = prices
            case 47 | 48 | 49 | 188 | 192 | 196:
                today = prices[: len(prices) // 2]
                tomorrow = prices[len(prices) // 2 : :]
        ret[day] = deviation_from_mean(today)
        ret[day + timedelta(days=1)] = deviation_from_mean(tomorrow)
        # todo: handle interim
        return ret

    @staticmethod
    def _set_price_mean(prices: list[float], adjusted_average: float | None) -> float:
        # print(f"adj: {adjusted_average}")
        if not adjusted_average:
            return mean(prices)
        return mean([adjusted_average, mean(prices)])
