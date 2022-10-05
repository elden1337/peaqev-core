import logging
from datetime import datetime
import statistics as stat
from ..top_up import top_up, TopUpDTO
from ....models.hourselection.const import (
    CAUTIONHOURTYPE_SUAVE,
    CAUTIONHOURTYPE_INTERMEDIATE,
    CAUTIONHOURTYPE
)
from .hoursselection_helpers import HourSelectionHelpers as helpers
from .hoursselection_helpers import HourSelectionInterimUpdate as interim
from .hoursselection_helpers import HourSelectionCalculations as calc
from ....models.hourselection.hourobject import HourObject, HourObjectExtended
from ....models.hourselection.hourselectionmodels import HourSelectionModel
from ....models.hourselection.hourtypelist import HourTypeList

_LOGGER = logging.getLogger(__name__)


class HourSelectionService:
    def __init__(self,
    model: HourSelectionModel, base_mock_hour: int = None):
        self.model = model
        self._base_mock_hour = base_mock_hour

    def update(
        self, 
        testhour:int = None
        ):
        if testhour is not None:
            self._base_mock_hour = testhour
        hours_ready = self._update_per_day(self.model.prices_today)
        hours = self._add_remove_limited_hours(hours_ready)
        hours_tomorrow = HourObject([],[],dict())
        if self.model.prices_tomorrow is not None and len(self.model.prices_tomorrow) > 0:
            self.model.options.conserve_top_up = False
            hours_tomorrow = self._add_remove_limited_hours(
                self._update_per_day(self.model.prices_tomorrow)
                )
            hours, hours_tomorrow = interim.interim_avg_update(
                hours, 
                hours_tomorrow, 
                self.model.prices_today, 
                self.model.prices_tomorrow, 
                self.model.options.absolute_top_price, 
                self.model.options.min_price
                )
        self.model.hours.hours_today = hours
        self.model.hours.hours_tomorrow = hours_tomorrow
        self.update_hour_lists(testhour=testhour)
 
    def _update_per_day(self, prices: list) -> HourObjectExtended:
        pricedict = dict
        if prices is not None and len(prices) > 1:
            pricedict = helpers._create_dict(prices)
            normalized_pricedict = helpers._create_dict(
                calc.normalize_prices(prices)
                )
            if stat.stdev(prices) > 0.05:
                prices_ranked = calc.rank_prices(pricedict, normalized_pricedict)
                ready_hours = self._determine_hours(prices_ranked, prices)
                return HourObjectExtended(
                    ready_hours.nh, 
                    ready_hours.ch, 
                    ready_hours.dyn_ch, 
                    pricedict
                    )
            return HourObjectExtended([], [], dict(), pricedict)

    def update_hour_lists(
        self, 
        testhour:int = None, 
        listtype:HourTypeList = None,
        ) -> None:
        hour = self.set_hour(testhour)
        if listtype is not None:
            match listtype:
                case HourTypeList.NonHour:
                    self._update_nonhour_list(hour)
                case HourTypeList.CautionHour:
                    self._update_cautionhour_list(hour)
                case HourTypeList.DynCautionHour:
                    self._update_dyn_cautionhour_dict(hour)
                case _:
                    pass
        else:
            self._update_nonhour_list(hour)
            self._update_cautionhour_list(hour)
            self._update_dyn_cautionhour_dict(hour)
        self._set_top_up(hour)
        
    def _update_nonhour_list(
        self, 
        hour:int
        ) -> None:
        hours_today = self.model.hours.hours_today 
        hours_tomorrow = self.model.hours.hours_tomorrow
        if self.model.options.conserve_top_up is False:
            self.model.hours.non_hours = []
            self.model.hours.non_hours.extend(h for h in hours_today.nh if h >= hour)
            self.model.hours.non_hours.extend(h for h in hours_tomorrow.nh if h < hour)
        else:
            self.model.hours.non_hours = [h for h in self.model.hours.non_hours if (hour >= 13 and h < hour) or h >= hour]
            
    def _update_cautionhour_list(
        self, 
        hour:int
        ) -> None:
        hours_today = self.model.hours.hours_today 
        hours_tomorrow = self.model.hours.hours_tomorrow
        if self.model.options.conserve_top_up is False:
            self.model.hours.caution_hours = []
            self.model.hours.caution_hours.extend(h for h in hours_today.ch if h >= hour)
            self.model.hours.caution_hours.extend(h for h in hours_tomorrow.ch if h < hour)
        else:
            self.model.hours.caution_hours = [h for h in self.model.hours.caution_hours if (hour >= 13 and h < hour) or h >= hour]

    def _update_dyn_cautionhour_dict(
        self, 
        hour:int
        ) -> None:
        hours_today = self.model.hours.hours_today 
        hours_tomorrow = self.model.hours.hours_tomorrow
        if self.model.options.conserve_top_up is False:
            self.model.hours.dynamic_caution_hours = dict()
            self.model.hours.dynamic_caution_hours.update({k: v for k, v in hours_today.dyn_ch.items() if k >= hour})
            self.model.hours.dynamic_caution_hours.update({k: v for k, v in hours_tomorrow.dyn_ch.items() if k < hour})
        else:
            self.model.hours.dynamic_caution_hours = {k: v for k, v in self.model.hours.dynamic_caution_hours.items()  if (hour >= 13 and k < hour) or k >= hour}

    def _set_top_up(
        self, 
        testhour: int = None
        ) -> None:
        if self.model.options.allow_top_up is True and self.model.prices_tomorrow is not None and len(self.model.prices_tomorrow) > 0:
            ret = top_up(TopUpDTO(
                raw_model=self.model,
                hour=self.set_hour(testhour)
                ))
            if ret.nh != self.model.hours.non_hours:
                self.model.options.conserve_top_up = True
                self.model.hours.non_hours = ret.nh
                self.model.hours.caution_hours = ret.ch
                self.model.hours.dynamic_caution_hours = ret.dyn_ch

    def _add_remove_limited_hours(self, hours: HourObjectExtended) -> HourObject:
        """Removes cheap hours and adds expensive hours set by user limitation"""
        if hours is None:
            return HourObject([],[],dict())

        if self.model.options.absolute_top_price is not None:
                ret = self._add_expensive_hours(hours)
        else: 
            ret = HourObject(hours.nh, hours.ch, hours.dyn_ch)
        if self.model.options.min_price > 0:
            ret = self._remove_cheap_hours(hours)
        return ret

    def _remove_cheap_hours(self, readyhours: HourObjectExtended) -> HourObject:
        lst = (h for h in readyhours.pricedict if readyhours.pricedict[h] < self.model.options.min_price)
        for h in lst:
            if h in readyhours.nh:
                readyhours.nh.remove(h)
            elif h in readyhours.ch:
                readyhours.ch.remove(h)
                readyhours.dyn_ch.pop(h)    
        return HourObject(readyhours.nh, readyhours.ch, readyhours.dyn_ch)

    def _add_expensive_hours(self, readyhours:HourObjectExtended) -> HourObject:
        lst = (h for h in readyhours.pricedict if readyhours.pricedict[h] >= self.model.options.absolute_top_price)
        for h in lst:
            if h not in readyhours.nh:
                readyhours.nh.append(h)
                if h in readyhours.ch:
                    readyhours.ch.remove(h)
                if len(readyhours.dyn_ch) > 0:
                    if h in readyhours.dyn_ch.keys():
                        readyhours.dyn_ch.pop(h)
        readyhours.nh.sort()
        return HourObject(readyhours.nh, readyhours.ch, readyhours.dyn_ch)

    def _determine_hours(self, price_list: dict, prices: list) -> HourObject:
        _nh = []
        _dyn_ch = dict()
        _ch = []
        for p in price_list:
            _permax = round(abs(price_list[p]["permax"] - 1), 2)
            if self.model.options.cautionhour_type == CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE]:
                _permax += 0.15
            elif self.model.options.cautionhour_type == CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE]:
                _permax += 0.05

            if float(price_list[p]["permax"]) <= self.model.options.cautionhour_type or float(price_list[p]["val"]) <= (sum(prices)/len(prices)):
                _ch.append(p)
                _dyn_ch[p] = round(_permax,2)
            else:
                _nh.append(p)
        return HourObject(_nh, _ch, _dyn_ch)

    def set_hour(self, testhour:int = None) -> int:
        return testhour if testhour is not None else self._base_mock_hour if self._base_mock_hour is not None else datetime.now().hour


# class Hourhelper:
#     _hour: int

#     @property
#     def hour(self):
#         return self._hour

#     @hour.setter
#     def hour(self, val:int = None):

#         #return testhour if testhour is not None else self._base_mock_hour if self._base_mock_hour is not None else datetime.now().hour
#         self._hour = val    