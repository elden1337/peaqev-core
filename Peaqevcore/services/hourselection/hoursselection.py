import logging
from typing import Tuple
from ...models.hourselection.const import (
    CAUTIONHOURTYPE_SUAVE,
    CAUTIONHOURTYPE_INTERMEDIATE,
    CAUTIONHOURTYPE
)
from .hourselectionservice.hoursselection_helpers import HourSelectionHelpers as helpers
from ...models.hourselection.hourselectionmodels import HourSelectionModel, HourSelectionOptions
from ...models.hourselection.hourtypelist import HourTypeList
from .hourselectionservice.hourselectionservice import HourSelectionService

_LOGGER = logging.getLogger(__name__)


class Hoursselection:
    def __init__(
            self,      
            absolute_top_price: float = 0,
            min_price: float = 0,
            cautionhour_type: float = CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE],
            base_mock_hour: int = None
    ):
        self.model = HourSelectionModel(
            options=HourSelectionOptions(
                cautionhour_type=cautionhour_type, 
                min_price=min_price,
                absolute_top_price=HourSelectionOptions.set_absolute_top_price(
                    absolute_top_price, 
                    min_price
                    )
                )
            )
        self.model.validate()
        self.service = HourSelectionService(self.model, base_mock_hour)
        self._adjusted_average = None
    
    @property
    def offsets(self) -> dict:
        return self.model.hours.offset_dict

    @property
    def non_hours(self) -> list:
        self.service.update_hour_lists(listtype=HourTypeList.NonHour)
        return self.model.hours.non_hours

    @property
    def caution_hours(self) -> list:
        self.service.update_hour_lists(listtype=HourTypeList.CautionHour)
        return self.model.hours.caution_hours

    @property
    def dynamic_caution_hours(self) -> dict:
        self.service.update_hour_lists(listtype=HourTypeList.DynCautionHour)
        return self.model.hours.dynamic_caution_hours

    @property
    def prices(self) -> list:
        return self.model.prices_today

    @prices.setter
    def prices(self, val):
        self.model.prices_today = val
        if self.prices == self.prices_tomorrow:
            self.prices_tomorrow = []
        else:
            self.update()

    @property
    def prices_tomorrow(self) -> list:
        return self.model.prices_tomorrow

    @prices_tomorrow.setter
    def prices_tomorrow(self, val):
        self.model.prices_tomorrow = helpers._convert_none_list(val)
        self.update()

    @property
    def adjusted_average(self):
        return self._adjusted_average

    @adjusted_average.setter
    def adjusted_average(self, val):
        self._adjusted_average = val

    def update(self, testhour:int = None) -> None:
        if testhour is not None:
            self.service._mock_hour = testhour
        self.service.update(adjusted_average=self.adjusted_average)

    def get_average_kwh_price(self):
        ret = self._get_charge_or_price()
        try:
            return round(sum(ret.values())/len(ret),2)
        except ZeroDivisionError as e:
                _LOGGER.warning(f"get_average_kwh_price_core could not be calculated: {e}")
        return 0
        
    def get_total_charge(self, currentpeak:float) -> float:
        ret = self._get_charge_or_price(currentpeak)
        return round(sum(ret.values()),1)

    def _get_charge_or_price(self, currentpeak:float = None) -> dict:
        hour = self.service.set_hour()
        ret = dict()

        def _looper_charge(h:int):
            if h in self.model.hours.dynamic_caution_hours:
                    ret[h] = self.model.hours.dynamic_caution_hours[h] * currentpeak
            elif h in self.model.hours.non_hours:
                ret[h] = 0
            else:
                ret[h] = currentpeak

        def _looper_price(h:int, tomorrow_active:bool):
            if h in self.model.hours.dynamic_caution_hours:
                    if tomorrow_active:
                        if h < hour and len(self.prices_tomorrow) > 0:
                            ret[h] = self.model.hours.dynamic_caution_hours[h] * self.prices_tomorrow[h]
                    if h >= hour:
                        ret[h] = self.model.hours.dynamic_caution_hours[h] * self.prices[h]
            elif h not in self.model.hours.non_hours:
                if h < hour and len(self.prices_tomorrow) > 0:
                    ret[h] = self.prices_tomorrow[h]
                if h >= hour:
                    ret[h] = self.prices[h]

        if self.prices_tomorrow is None or len(self.prices_tomorrow) < 1:
            for h in range(hour,24):
                if currentpeak is not None:
                    _looper_charge(h)
                else:
                    _looper_price(h, False)
        else:
            for h in range(hour,(hour+24)):
                h = h-24 if h > 23 else h
                if currentpeak is not None:
                    _looper_charge(h)
                else:
                    _looper_price(h, True)
        return ret

    # def _get_charge_or_price(self, currentpeak:float = None) -> Tuple[dict, dict]:
    #     hour = self.service.set_hour()
    #     if currentpeak is not None:
    #         self.current_peak = currentpeak
    #     total_prices = self.prices
    #     total_prices.append(self.prices_tomorrow)

    #     def _looper_charge(_range: range) -> dict:
    #         _chargeret = {}
    #         for h in _range:
    #             if h in self.model.hours.dynamic_caution_hours:
    #                     _chargeret[h] = self.model.hours.dynamic_caution_hours[h] * self.current_peak
    #             elif h in self.model.hours.non_hours:
    #                 _chargeret[h] = 0
    #             else:
    #                 _chargeret[h] = self.current_peak
    #         return _chargeret

    #     def _looper_price(_range: range, tomorrow_active:bool) -> dict:
    #         _priceret = {}
    #         for h in _range:
    #             print(h)

    #             if h in self.model.hours.dynamic_caution_hours:
    #                     if tomorrow_active:
    #                         if h < hour and len(self.prices_tomorrow) > 0:
    #                             _priceret[h] = self.model.hours.dynamic_caution_hours[h] * total_prices[h]
    #                     if h >= hour:
    #                         _priceret[h] = self.model.hours.dynamic_caution_hours[h] * total_prices[h]
    #             elif h not in self.model.hours.non_hours:
    #                 if h < hour and len(self.prices_tomorrow) > 0:
    #                     _priceret[h] = total_prices[h]
    #                 if h >= hour:
    #                     _priceret[h] = total_prices[h]
    #         return _priceret

    #     search_range = range(0,24) if self.prices_tomorrow is None or len(self.prices_tomorrow) < 1 else range(hour, (hour+24))
    #     return _looper_price(search_range, True if search_range[-1] > 24 else False), _looper_charge(search_range)