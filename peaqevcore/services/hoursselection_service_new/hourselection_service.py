from .models.stop_string import AllowanceObj, set_allowance_obj
from .models.datetime_model import DateTimeModel
from .models.hour_price import HourPrice
from .models.hourselection_model import HourSelectionModel
from statistics import stdev, mean, variance
from datetime import date, datetime, timedelta
from ...models.hourselection.hourselection_options import HourSelectionOptions
from .hourselection_calculations import normalize_prices
from .offset_dict import get_offset_dict, set_offset_dict
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
        for r in self.model.hours_prices:
            print(r.dt, r.passed, r.permittance)
        ret = [hp for hp in self.model.hours_prices if not hp.passed]
        # if self.max_min.active:
        #     for r in ret:
        #         r.permittance = 0.0 if r.dt in self.max_min.non_hours else 1.0
        return ret

    @property
    def passed_hours(self) -> list[HourPrice]:
        self.update()
        return [hp for hp in self.model.hours_prices if hp.passed]

    @property
    def stopped_string(self) -> str:
        self.update()
        return self.allowance.display_name

    @property
    def allowance(self) -> AllowanceObj:
        return set_allowance_obj(self.dtmodel, self.future_hours)

    @property
    def average_kwh_price(self) -> float:
        return round(
            mean(
                [
                    hp.permittance * hp.price
                    for hp in self.future_hours
                    if hp.permittance > 0
                ]
            ),
            2,
        )

    @property
    def offset_dict(self) -> dict:
        return get_offset_dict(self._offset_dict)

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
                return await self.async_create_hour_prices(
                    prices, prices_tomorrow, False
                )
            case 92 | 96 | 100:
                return await self.async_create_hour_prices(
                    prices, prices_tomorrow, True
                )
            case 0:
                return []
        raise ValueError(
            f"Length of pricelist must be either 23,24,25,92,96 or 100. Your length is {len(prices)}"
        )

    def _is_passed(self, datum, hour, quarter) -> bool:
        if datum == self.dtmodel.hdate_tomorrow:
            return False
        if self.dtmodel.hour > hour:
            return True
        elif self.dtmodel.hour == hour:
            if self.dtmodel.quarter > quarter:
                return True
        return False

    async def async_create_hour_prices(
        self,
        prices: list[float],
        prices_tomorrow: list[float] = [],
        is_quarterly: bool = False,
    ) -> list:
        # todo: handle here first if prices or prices_tomorrow are 92 or 100 in length (dst shift)
        ret = []
        ret.extend(self._set_hourprice_list(prices, is_quarterly, self.dtmodel.hdate))
        ret.extend(
            self._set_hourprice_list(
                prices_tomorrow, is_quarterly, self.dtmodel.hdate_tomorrow
            )
        )
        return await self.async_set_permittance(ret)

    def _set_hourprice_list(
        self, prices: list, is_quarterly: bool, datum: date
    ) -> list[HourPrice]:
        ret = []
        for idx, p in enumerate(prices):
            assert isinstance(p, (float, int))
            hour = int(idx / 4) if is_quarterly else idx
            quarter = idx % 4 if is_quarterly else 0
            ret.append(
                HourPrice(
                    day=datum,
                    hour=hour,
                    quarter=quarter,
                    price=p,
                    passed=self._is_passed(datum, hour, quarter),
                    hour_type=HourPrice.set_hour_type(
                        self.options.absolute_top_price, self.options.min_price, p
                    ),
                )
            )
        return ret

    async def async_set_permittance(
        self, hour_prices: list[HourPrice]
    ) -> list[HourPrice]:
        prices = normalize_prices([hp.price for hp in hour_prices])
        hours_permitted = set_scooped_permittance(
            set_initial_permittance(
                hour_prices,
                self._set_price_mean(prices, self.model.adjusted_average),
                stdev(prices),
            ),
            self.options.cautionhour_type_enum,
        )
        self._offset_dict = set_offset_dict(prices, hours_permitted[0].day)
        return hours_permitted

    @staticmethod
    def _set_price_mean(prices: list[float], adjusted_average: float | None) -> float:
        # print(f"adj: {adjusted_average}")
        if not adjusted_average:
            return mean(prices)
        return mean([adjusted_average, mean(prices)])
