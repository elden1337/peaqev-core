import logging
from typing import Tuple
from ...models.hourselection.cautionhourtype import CautionHourType
from ...models.hourselection.hourselection_model import HourSelectionModel
from ...models.hourselection.hourselection_options import HourSelectionOptions
from ..hoursselection_service_new.hourselection_service import HourSelectionService

from datetime import datetime

_LOGGER = logging.getLogger(__name__)


class Hoursselection:
    def __init__(
        self,
        absolute_top_price: float = 0,
        min_price: float = 0,
        cautionhour_type: str | CautionHourType = CautionHourType.SUAVE.value,
    ):
        self.cautionhour_type_enum = (
            CautionHourType(cautionhour_type.lower())
            if isinstance(cautionhour_type, str)
            else cautionhour_type
        )
        self.model = HourSelectionModel(
            options=HourSelectionOptions(
                cautionhour_type_enum=self.cautionhour_type_enum,
                min_price=min_price,
                top_price=absolute_top_price
            )
        )
        self.model.validate()
        self.service = HourSelectionService(options=self.model.options)

    @property
    def offsets(self) -> dict:
        ret = {}
        ret["today"] = self.service.offset_dict["today"]
        ret["tomorrow"] = self.service.offset_dict["tomorrow"]
        return ret

    @property
    def caution_hours(self) -> list[datetime]:
        return sorted(list(self.dynamic_caution_hours.keys()))

    @property
    def non_hours(self) -> list[datetime]:
        self.service.update()
        return [hp.dt for hp in self.future_hours if hp.permittance == 0.0]

    @property
    def dynamic_caution_hours(self) -> dict[datetime, float]:
        self.service.update()
        ret = {
            hp.dt: hp.permittance
            for hp in self.future_hours
            if 0.0 < hp.permittance < 1.0
        }
        keys = list(ret.keys())
        keys.sort()
        return {k: ret[k] for k in keys}

    @property
    def future_hours(self) -> list:
        return self.service.display_future_hours

    @property
    def prices(self) -> list:
        return self.service.model.prices_today

    @property
    def prices_tomorrow(self) -> list:
        return self.service.model.prices_tomorrow

    @property
    def adjusted_average(self):
        return self.model.adjusted_average

    @adjusted_average.setter
    def adjusted_average(self, val):
        if val != self.model.adjusted_average:
            self.model.adjusted_average = val

    async def async_update_adjusted_average(self, val):
        await self.service.async_update_adjusted_average(val)
        
    async def async_update_top_price(self, dyn_top_price=None) -> None:
        await self.model.options.async_set_absolute_top_price(dyn_top_price)
        await self.async_update_prices(self.prices, self.prices_tomorrow)

    async def async_update_prices(self, prices: list, prices_tomorrow: list = []):
        await self.service.async_update_prices(prices, prices_tomorrow)

    async def async_get_average_kwh_price(self) -> Tuple[float | None, float | None]:
        ret_static = self.service.average_kwh_price
        ret_dynamic = self.service.max_min.average_price
        if ret_dynamic is not None:
            if ret_dynamic > ret_static:
                ret_dynamic = ret_static
        return ret_static, ret_dynamic

    async def async_get_total_charge(
        self, currentpeak: float
    ) -> Tuple[float, float | None]:
        ret_dynamic = self.service.max_min.total_charge
        self.model.current_peak = currentpeak
        _charge = (
            self.service.max_min.model.expected_hourly_charge
            if self.service.max_min.active
            else currentpeak
        )
        ret_static = round(
            sum([hp.permittance * _charge for hp in self.service.future_hours]),
            1,
        )
        if ret_dynamic is not None:
            if ret_dynamic > ret_static:
                ret_dynamic = ret_static
        return ret_static, ret_dynamic
