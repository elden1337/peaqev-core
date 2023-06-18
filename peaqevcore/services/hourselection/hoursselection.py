import logging
from statistics import mean
from typing import Tuple
from ...models.hourselection.cautionhourtype import CautionHourType
from ...models.hourselection.hourselection_model import HourSelectionModel
from ...models.hourselection.hourselection_options import HourSelectionOptions
from ...models.hourselection.hourtypelist import HourTypeList
from ..hoursselection_service_new.hourselection_service import HourSelectionService
from .hourselectionservice.hoursselection_helpers import convert_none_list
from .hourselectionservice.max_min_charge import MaxMinCharge

_LOGGER = logging.getLogger(__name__)


class Hoursselection:
    def __init__(
        self,
        absolute_top_price: float = 0,
        min_price: float = 0,
        cautionhour_type: str | CautionHourType = CautionHourType.SUAVE.value,
        blocknocturnal: bool = False,
        base_mock_hour: int | None = None,
    ):
        self.cautionhour_type_enum = (
            CautionHourType(cautionhour_type.lower())
            if isinstance(cautionhour_type, str)
            else cautionhour_type
        )
        self.model = HourSelectionModel(
            options=HourSelectionOptions(
                cautionhour_type=CautionHourType.get_num_value(cautionhour_type),
                cautionhour_type_enum=self.cautionhour_type_enum,
                min_price=min_price,
                top_price=absolute_top_price,
                blocknocturnal=blocknocturnal,
            )
        )
        self.model.validate()
        self.service = HourSelectionService(options=self.model.options)
        self.max_min: MaxMinCharge = MaxMinCharge(self, self.model.options.min_price)

    @property
    def offsets(self) -> dict:
        ret = {}
        ret["today"] = self.service.offset_dict["today"]
        ret["tomorrow"] = self.service.offset_dict["tomorrow"]
        return ret

    @property
    def non_hours(self) -> list:
        if self.max_min.active:
            return self.max_min.non_hours
        return self.internal_non_hours

    @property
    def caution_hours(self) -> list:
        return [k.hour for k, v in self.service.dynamic_caution_hours.items()]
        # self.model.hours.update_hour_list(
        #     listtype=HourTypeList.CautionHour, hour=self.service.set_hour()
        # )
        # return self.model.hours.caution_hours

    @property
    def dynamic_caution_hours(self) -> dict:
        if self.max_min.active:
            return self.max_min.dynamic_caution_hours
        return self.internal_dynamic_caution_hours

    @property
    def internal_non_hours(self) -> list:
        # self.model.hours.update_hour_list(
        #     listtype=HourTypeList.NonHour, hour=self.service.set_hour()
        # )
        # return self.model.hours.non_hours
        self.service.update()
        return self.service.non_hours

    @property
    def internal_dynamic_caution_hours(self) -> dict:
        self.service.update()
        return self.service.dynamic_caution_hours

    @property
    def prices(self) -> list:
        return self.model.prices_today

    @prices.setter
    def prices(self, val):
        self.model.prices_today = val
        if self.prices == self.prices_tomorrow:
            self.prices_tomorrow = []

    @property
    def prices_tomorrow(self) -> list:
        return self.model.prices_tomorrow

    @prices_tomorrow.setter
    def prices_tomorrow(self, val):
        ret = convert_none_list(val)
        self.model.prices_tomorrow = ret

    @property
    def adjusted_average(self):
        return self.model.adjusted_average

    @adjusted_average.setter
    def adjusted_average(self, val):
        if val != self.model.adjusted_average:
            self.model.adjusted_average = val

    async def async_update_adjusted_average(self, val):
        # self.adjusted_average = val
        await self.service.async_update_adjusted_average(val)
        # await self.async_update_prices(self.prices, self.prices_tomorrow)

    async def async_update_top_price(self, dyn_top_price=None) -> None:
        await self.model.options.async_set_absolute_top_price(dyn_top_price)
        await self.async_update_prices(self.prices, self.prices_tomorrow)

    async def async_update_prices(self, prices: list, prices_tomorrow: list = []):
        max_min: bool = False
        if any([self.prices != prices, self.prices_tomorrow != prices_tomorrow]):
            max_min = True
        self.prices = prices
        self.prices_tomorrow = prices_tomorrow
        await self.service.async_update_prices(self.prices, self.prices_tomorrow)

    async def async_get_average_kwh_price(self) -> Tuple[float | None, float | None]:
        ret_dynamic = None
        if self.max_min.active:
            ret_dynamic = self.max_min.average_price
            ret_static = self.max_min.original_average_price
            return ret_static, ret_dynamic
        else:
            ret_static = mean(
                [hp.permittance * hp.price for hp in self.service.future_hours]
            )
            try:
                return round(ret_static, 2), ret_dynamic
            except ZeroDivisionError as e:
                _LOGGER.warning(
                    f"get_average_kwh_price_core could not be calculated: {e}"
                )
            return 0, None

    async def async_get_total_charge(
        self, currentpeak: float
    ) -> Tuple[float, float | None]:
        ret_dynamic = None
        if self.max_min.active:
            ret_dynamic = self.max_min.total_charge
            # ret_static = self.max_min.original_total_charge
            # return ret_static, ret_dynamic
        # else:
        self.model.current_peak = currentpeak
        ret_static = sum(
            [hp.permittance * currentpeak for hp in self.service.future_hours]
        )
        return round(ret_static, 1), ret_dynamic
