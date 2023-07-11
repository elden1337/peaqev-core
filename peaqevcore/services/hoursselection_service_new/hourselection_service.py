from .models.stop_string import AllowanceObj, set_allowance_obj
from .models.datetime_model import DateTimeModel
from .models.hour_price import HourPrice
from .models.hourselection_model import HourSelectionModel
from statistics import stdev, mean
from ...models.hourselection.hourselection_options import HourSelectionOptions
from .hourselection_calculations import normalize_prices, block_nocturnal
from .permittance import (
    set_initial_permittance,
    set_scooped_permittance,
    set_min_allowed_hours,
)
from .max_min_charge import MaxMinCharge


class HourSelectionService:
    def __init__(self, options: HourSelectionOptions = HourSelectionOptions()):
        self.options = options
        self.use_quarters: bool = False
        self.dtmodel = DateTimeModel()
        self.model = HourSelectionModel()
        self.max_min = MaxMinCharge(service=self, min_price=self.options.min_price)

    @property
    def all_hours(self) -> list[HourPrice]:
        self.update()
        return self.model.hours_prices

    @property
    def future_hours(self) -> list[HourPrice]:
        self.update()
        return self.get_future_hours()

    @property
    def display_future_hours(self) -> list[HourPrice]:
        if self.max_min.active and not self.max_min.overflow:
            return self.max_min.future_hours
        return self.future_hours

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
        return set_allowance_obj(self.dtmodel, self.display_future_hours)

    @property
    def average_kwh_price(self) -> float:
        return round(self.get_average_kwh_price(), 2)

    @property
    def offset_dict(self) -> dict:
        return self.model.get_offset_dict(self.dtmodel.dt)

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
            return mean(
                [
                    hp.permittance * hp.price
                    for hp in self.future_hours
                    if hp.permittance > 0
                ]
            )
        except Exception:
            return 0.0

    def get_future_hours(self) -> list[HourPrice]:
        for hp in self.model.hours_prices:
            hp.set_passed(self.dtmodel)
        return [hp for hp in self.model.hours_prices if not hp.passed]

    async def async_update_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ):
        self.model.prices_today = prices  # clean first
        self.model.prices_tomorrow = prices_tomorrow  # clean first
        if self._do_recalculate_prices(prices, prices_tomorrow):
            self._create_prices(prices, prices_tomorrow)
            if self.max_min.active:
                self.max_min.get_hours()
        else:
            await self.async_update()

    async def async_update_adjusted_average(self, adjusted_average: float) -> None:
        self.model.adjusted_average = adjusted_average
        self.update()
        if len(self.model.hours_prices) > 0:
            self._set_permittance()
        else:
            await self.async_update()

    def _do_recalculate_prices(self, prices, prices_tomorrow) -> bool:
        if [
            hp.price
            for hp in self.model.hours_prices
            if hp.dt.date() == self.dtmodel.hdate
        ] == prices and len(prices_tomorrow) < 1:
            return False
        return True

    def _create_prices(
        self, prices: list[float], prices_tomorrow: list[float] = []
    ) -> None:
        # todo: fix to allow 23, 24,25, 92, 96, 100 for dst-dates.
        self.model.hours_prices = []
        match len(prices):
            case 23 | 24 | 25:
                self._create_hour_prices(prices, prices_tomorrow, is_quarterly=False)
            case 92 | 96 | 100:
                self._create_hour_prices(prices, prices_tomorrow, is_quarterly=True)
            case _:
                raise ValueError(
                    f"Length of pricelist must be either 23,24,25,92,96 or 100. Your length is {len(prices)}"
                )

    def _create_hour_prices(
        self,
        prices: list[float],
        prices_tomorrow: list[float] = [],
        is_quarterly: bool = False,
    ) -> None:
        # todo: handle here first if prices or prices_tomorrow are 92 or 100 in length (dst shift)
        self.model.use_quarters = is_quarterly
        self.model.set_hourprice_list(
            prices,
            self.options,
            self.dtmodel.hdate,
            self.dtmodel.is_passed,
        )
        self.model.set_hourprice_list(
            prices_tomorrow,
            self.options,
            self.dtmodel.hdate_tomorrow,
            self.dtmodel.is_passed,
        )
        self._set_permittance()
        block_nocturnal(self.model.hours_prices, self.options.blocknocturnal)

    def _set_permittance(self) -> None:
        prices = normalize_prices(
            [
                hp.price
                for hp in self.model.hours_prices
                if hp.dt.date() >= self.dtmodel.hdate
            ]
        )
        self.model.set_offset_dict(prices, self.dtmodel.dt.date())
        set_initial_permittance(
            self.model.hours_prices,
            self.model.adjusted_average,
        )
        set_scooped_permittance(
            self.model.hours_prices,
            self.options.cautionhour_type_enum,
        )
        set_min_allowed_hours(
            self.model.hours_prices,
            self.options.cautionhour_type_enum,
        )
