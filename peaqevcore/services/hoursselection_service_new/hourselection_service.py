from datetime import date, time, timedelta, datetime
import logging
from .models.stop_string import AllowanceObj, set_allowance_obj
from .models.datetime_model import DateTimeModel
from .models.hour_price import HourPrice
from .models.hourselection_service_model import HourSelectionServiceModel
from ...models.hourselection.hourselection_options import HourSelectionOptions
from .hourselection_calculations import normalize_prices, do_recalculate_prices, get_average_kwh_price
from .permittance import (
    set_initial_permittance,
    set_scooped_permittance,
    set_blank_permittance,
    set_min_allowed_hours,
)
from statistics import stdev, mean
from .max_min_charge import MaxMinCharge

_LOGGER = logging.getLogger(__name__)

class HourSelectionService:
    def __init__(self, options: HourSelectionOptions = HourSelectionOptions()):
        self.options = options
        self.dtmodel = DateTimeModel()
        self.model = HourSelectionServiceModel()
        self.max_min = MaxMinCharge(service=self, min_price=self.options.min_price)

    @property
    def all_hours(self) -> list[HourPrice]:
        self.update()
        return self.model.hours_prices

    @property
    def future_hours(self) -> list[HourPrice]:
        self.update()
        return self.model.get_future_hours(self.dtmodel)

    @property
    def display_future_hours(self) -> list[HourPrice]:
        if self.max_min.active:
            return self.max_min.future_hours(self.dtmodel)
        return self.future_hours

    @property
    def allowance(self) -> AllowanceObj:
        self.update()
        return set_allowance_obj(self.dtmodel, self.display_future_hours)

    @property
    def average_kwh_price(self) -> float:
        return round(get_average_kwh_price(self.future_hours), 2)

    @property
    def offset_dict(self) -> dict:
        return self.model.get_offset_dict(self.dtmodel.dt)

    def update(self):  
        self.model.hours_prices = [hp for hp in self.model.hours_prices if hp.dt.date() >= self.dtmodel.hdate]        
        for hp in self.model.hours_prices:            
            hp.set_passed(self.dtmodel)        
        if len(self.model.get_future_hours(self.dtmodel)) >= 24:
            set_scooped_permittance(
                self.model.get_future_hours(self.dtmodel), self.options.cautionhour_type_enum
            )        

    async def async_update(self):
        self.update()

    def clean_prices(self, prices, prices_tomorrow) -> dict:
        hours_today = self.dtmodel.get_eligable_hours(self.dtmodel.hdate)
        price_dict: dict = {}
        for idx, h in enumerate(hours_today):
            try:
                price_dict[h] = prices[idx]
            except Exception as e:
                _LOGGER.exception(f"Exception in adding prices today! {e}")
                raise
        if len(prices_tomorrow):
            hours_tomorrow = self.dtmodel.get_eligable_hours(self.dtmodel.hdate_tomorrow)
            for idx, h in enumerate(hours_tomorrow):
                try:
                    price_dict[h] = prices_tomorrow[idx]
                except Exception as e:
                    _LOGGER.exception(f"Exception in adding prices tomorrow! {e}")
                    raise
        return price_dict

    async def async_update_prices(self, prices: list[float], prices_tomorrow: list[float] = []) -> None:

        try:
            price_dict = self.clean_prices(prices, prices_tomorrow)
            self.model.prices_today = prices  # clean first
            self.model.prices_tomorrow = prices_tomorrow  # clean first

            if do_recalculate_prices(price_dict=price_dict, hours_prices=self.model.hours_prices, hdate=self.dtmodel.hdate):
                self._create_prices(prices, prices_tomorrow)
            else:
                print(f"NOT recalculate prices {len(prices)} {len(prices_tomorrow)}")
                _LOGGER.debug(f"NOT recalculate prices {len(prices)} {len(prices_tomorrow)}")
                await self.async_update()
            self.max_min.get_hours()
        except Exception as e:
            _LOGGER.exception(f"Exception in updating prices! Please report a bug and include the following: {e}")

    async def async_update_adjusted_average(self, adjusted_average: float) -> None:
        self.model.adjusted_average = adjusted_average
        self.update()
        if len(self.model.hours_prices) > 0:
            self._set_permittance()
        else:
            await self.async_update()

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
        prices_tomorrow=None,
        is_quarterly: bool = False,
    ) -> None:
        # todo: handle here first if prices or prices_tomorrow are 92 or 100 in length (dst shift)
        if prices_tomorrow is None:
            prices_tomorrow = []
        self.model.use_quarters = is_quarterly
        self.model.set_hourprice_lists(prices, prices_tomorrow, self.options, self.dtmodel.hdate, self.dtmodel.hdate_tomorrow, self.dtmodel.is_passed, self.dtmodel.get_eligable_hours)
        self._set_permittance()

    def _set_permittance(self) -> None:
        prices = normalize_prices(
            [
                hp.price
                for hp in self.model.hours_prices
                if hp.dt.date() >= self.dtmodel.hdate
            ]
        )
        self.model.set_offset_dict(prices, self.dtmodel.dt.date(), self.options.min_price)
        if not self.is_flat([h.price for h in self.model.hours_prices if not h.passed]):
            set_initial_permittance(
                self.model.hours_prices,
                self.model.adjusted_average,
                self.options.non_hours
            )
        else:
            set_blank_permittance(self.model.hours_prices)
        set_scooped_permittance(
            self.model.hours_prices,
            self.options.cautionhour_type_enum,
        )
        set_min_allowed_hours(
            self.model.hours_prices,
            self.options.cautionhour_type_enum,
        )

    @staticmethod
    def is_flat(prices: list[float]) -> bool:
        """if the fsd is below a score of 8(%) it is considered flat"""
        return stdev(prices)*100/mean(prices) < 8