from .models.stop_string import AllowanceObj, set_allowance_obj
from .models.datetime_model import DateTimeModel
from .models.hour_price import HourPrice
from .models.list_type import ListType
from .models.hourselection_model import HourSelectionModel
from statistics import stdev, mean
from datetime import date, datetime, time
from ...models.hourselection.hourselection_options import HourSelectionOptions
from .hourselection_calculations import normalize_prices
from .offset_dict import get_offset_dict, set_offset_dict
from .permittance import set_initial_permittance, set_scooped_permittance
from .max_min_charge import MaxMinCharge


class HourSelectionService:
    def __init__(self, options: HourSelectionOptions = HourSelectionOptions()):
        self.options = options
        self.use_quarters: bool = False
        self.dtmodel = DateTimeModel()
        self.model = HourSelectionModel()
        self.max_min = MaxMinCharge(service=self, min_price=self.options.min_price)
        self._offset_dict: dict[datetime, dict] = {}

    @property
    def all_hours(self) -> list[HourPrice]:
        self.update()
        return self.model.hours_prices

    @property
    def future_hours(self) -> list[HourPrice]:
        self.update()
        return self.get_future_hours()

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
        return self.get_average_kwh_price()

    @property
    def offset_dict(self) -> dict:
        return get_offset_dict(self._offset_dict)

    def update(self):
        for hp in self.model.hours_prices:
            hp.set_passed(self.dtmodel)
        if len(self.get_future_hours()) >= 24:
            set_scooped_permittance(
                self.get_future_hours(), self.options.cautionhour_type_enum
            )

    async def async_update(self):
        self.update()

    def get_average_kwh_price(self) -> float:
        try:
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
        except Exception:
            return 0.0

    def get_future_hours(self) -> list[HourPrice]:
        ret = [hp for hp in self.model.hours_prices if not hp.passed]
        if self.max_min.active:
            for r in ret:
                if r in self.max_min.non_hours:
                    r.permittance = 0.0
                elif r.dt in self.max_min.dynamic_caution_hours.keys():
                    r.permittance = self.max_min.dynamic_caution_hours[r.dt]
        return ret

    async def async_update_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ):
        self.model.prices_today = prices  # clean first
        self.model.prices_tomorrow = prices_tomorrow  # clean first
        if self._do_recalculate_prices(prices, prices_tomorrow):
            await self.async_create_prices(prices, prices_tomorrow)

    async def async_update_adjusted_average(self, adjusted_average: float) -> None:
        self.model.adjusted_average = adjusted_average
        self.update()
        if len(self.model.hours_prices) > 0:
            self._set_permittance()

    def _do_recalculate_prices(self, prices, prices_tomorrow) -> bool:
        if [
            hp.price
            for hp in self.model.hours_prices
            if hp.dt.date() == self.dtmodel.hdate
        ] == prices and len(prices_tomorrow) < 1:
            return False
        return True

    async def async_create_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> None:
        # todo: fix to allow 23, 24,25, 92, 96, 100 for dst-dates.
        self.model.hours_prices = []
        match len(prices):
            case 23 | 24 | 25:
                await self.async_create_hour_prices(
                    prices, prices_tomorrow, is_quarterly=False
                )
            case 92 | 96 | 100:
                await self.async_create_hour_prices(
                    prices, prices_tomorrow, is_quarterly=True
                )
            case _:
                raise ValueError(
                    f"Length of pricelist must be either 23,24,25,92,96 or 100. Your length is {len(prices)}"
                )

    async def async_create_hour_prices(
        self,
        prices: list[float],
        prices_tomorrow: list[float] = [],
        is_quarterly: bool = False,
    ) -> None:
        # todo: handle here first if prices or prices_tomorrow are 92 or 100 in length (dst shift)
        self.use_quarters = is_quarterly
        self.model.set_hourprice_list(
            prices,
            self.options,
            is_quarterly,
            self.dtmodel.hdate,
            self.dtmodel.is_passed,
        )
        self.model.set_hourprice_list(
            prices_tomorrow,
            self.options,
            is_quarterly,
            self.dtmodel.hdate_tomorrow,
            self.dtmodel.is_passed,
        )
        self._set_permittance()

    def _set_permittance(self) -> None:
        prices = normalize_prices([hp.price for hp in self.model.hours_prices])
        set_initial_permittance(
            self.model.hours_prices,
            mean(prices),
            stdev(prices),
            self.model.adjusted_average,
        )
        set_scooped_permittance(
            self.model.hours_prices,
            self.options.cautionhour_type_enum,
        )
        self._offset_dict = set_offset_dict(
            prices, self.model.hours_prices[0].dt.date()
        )
        self._block_nocturnal(self.model.hours_prices, self.options.blocknocturnal)

    @staticmethod
    def _block_nocturnal(
        hour_prices: list[HourPrice], block_nocturnal: bool = False
    ) -> None:
        blockhours = [23, 0, 1, 2, 3, 4, 5, 6]
        if block_nocturnal:
            for hp in hour_prices:
                if hp.hour in blockhours:
                    hp.permittance = 0.0
