import logging
from datetime import datetime
from typing import Tuple
import statistics as stat
from ....models.hourselection.const import (
    CAUTIONHOURTYPE_SUAVE,
    CAUTIONHOURTYPE_INTERMEDIATE,
    CAUTIONHOURTYPE_AGGRESSIVE,
    CAUTIONHOURTYPE
)
from .hoursselection_helpers import HourSelectionHelpers as helpers
from .hoursselection_helpers import HourSelectionCalculations as calc
from ....models.hourselection.hourobject import HourObject
from ....models.hourselection.hourselectionmodels import HourSelectionModel
from ....models.hourselection.hourtypelist import HourTypeList

_LOGGER = logging.getLogger(__name__)

ALLOWANCE_SCHEMA = {
            CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE]: 1.15,
            CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE]: 1.05,
            CAUTIONHOURTYPE[CAUTIONHOURTYPE_AGGRESSIVE]: 1
        }

class HourSelectionService:
    def __init__(self,
    model: HourSelectionModel, base_mock_hour: int = None):
        self.model = model
        self._mock_hour = base_mock_hour

    def update(
        self
    ) -> None:
        hours, hours_tomorrow = self.interim_day_update(
            today=self._update_per_day(prices=self.model.prices_today), 
            tomorrow=self._update_per_day(prices=self.model.prices_tomorrow)
            )
        self.model.hours.hours_today = self._add_remove_limited_hours(hours)
        self.model.hours.hours_tomorrow = self._add_remove_limited_hours(hours_tomorrow)
        self.update_hour_lists()

    def _update_per_day(self, prices: list) -> HourObject:
        pricedict = {}
        if prices is not None and len(prices) > 1:
            pricedict = helpers._create_dict(prices)
            normalized_pricedict = helpers._create_dict(
                calc.normalize_prices(prices)
                )
            if stat.stdev(prices) > 0.05:
                ready_hours = self._determine_hours(
                    calc.rank_prices(
                        pricedict, 
                        normalized_pricedict,
                        self.model.adjusted_average
                        ), 
                        prices
                        )
                ret= HourObject(
                    nh=ready_hours.nh, 
                    ch=ready_hours.ch, 
                    dyn_ch=ready_hours.dyn_ch, 
                    pricedict=pricedict
                    )
            else:
                ret= HourObject(nh=[], ch=[], dyn_ch={},pricedict=pricedict)
            ret.offset_dict=calc.get_offset_dict(normalized_pricedict)
            return ret
        return HourObject([],[],{})

    def update_hour_lists(
        self, 
        listtype:HourTypeList = None,
        ) -> None:
        hour = self.set_hour()
        if listtype is not None:
            match listtype:
                case HourTypeList.NonHour:
                    self.model.hours.update_non_hours(hour)
                case HourTypeList.CautionHour:
                    self.model.hours.update_caution_hours(hour)
                case HourTypeList.DynCautionHour:
                    self.model.hours.update_dynanmic_caution_hours(hour)   
                case _:
                    pass
        else:
            self.model.hours.update_non_hours(hour)
            self.model.hours.update_caution_hours(hour)
            self.model.hours.update_dynanmic_caution_hours(hour)
            self.model.hours.update_offset_dict()

    def _add_remove_limited_hours(self, hours: HourObject) -> HourObject:
        """Removes cheap hours and adds expensive hours set by user limitation"""
        if hours is None or all([len(hours.nh) == 0, len(hours.ch) == 0, len(hours.dyn_ch) == 0]):
            return HourObject([],[],{})
        hours.add_expensive_hours(self.model.options.absolute_top_price)
        hours.remove_cheap_hours(self.model.options.min_price)
        return hours

    def _determine_hours(self, price_list: dict, prices: list) -> HourObject:
        ret = HourObject([],[],{})
        for p in price_list:
            _permax = self._set_charge_allowance(price_list[p]["permax"])
            if self._should_be_cautionhour(price_list[p], prices):
                ret.ch.append(p)
                ret.dyn_ch[p] = round(_permax,2)
            else:
                ret.nh.append(p)
        return ret

    def _should_be_cautionhour(self, price_item, prices) -> bool:
        first = any([
                    float(price_item["permax"]) <= self.model.options.cautionhour_type,
                    float(price_item["val"]) <= (sum(prices)/len(prices))
                ])
        second = (self.model.current_peak > 0 and self.model.current_peak*price_item["permax"] > 1) or self.model.current_peak == 0
        return all([first, second])

    def _set_charge_allowance(self, price_input) -> float:
        _allowance = round(abs(price_input - 1), 2)
        return _allowance * ALLOWANCE_SCHEMA[self.model.options.cautionhour_type]
        
    def set_hour(self, testhour:int = None) -> int:
        return testhour if testhour is not None else self._mock_hour if self._mock_hour is not None else datetime.now().hour

    def interim_day_update(self, today: HourObject, tomorrow: HourObject) -> Tuple[HourObject, HourObject]:
        if len(self.model.prices_tomorrow) == 0:
            return today, tomorrow
        avg = self._get_average_price()
        _today = self._set_interim_per_day(
            True,
            avg, 
            self.model.prices_today, 
            today
            )
        _tomorrow = self._set_interim_per_day(
            False,
            avg, 
            self.model.prices_tomorrow, 
            tomorrow
            )
        return _today, _tomorrow

    def _set_interim_per_day(
        self,
        is_today: bool,
        avg: float, 
        prices: list, 
        hour_obj: HourObject, 
        ) -> HourObject:
        new_nonhours = []
        new_ok_hours = []

        for idx, p in enumerate(prices):
            if (idx >= 14 and is_today) or idx < 14:
                if p > avg:
                    new_nonhours.append(idx)
                elif p <= avg:
                    new_ok_hours.append(idx)
        for h in new_nonhours:
            if h not in hour_obj.nh:
                hour_obj.nh.append(h)
                if h in hour_obj.ch:
                    hour_obj.ch.remove(h)
                if len(hour_obj.dyn_ch) > 0:
                    if h in hour_obj.dyn_ch.keys():
                        hour_obj.dyn_ch.pop(h)
        hour_obj.nh.sort()

        for h in new_ok_hours:
            if h in hour_obj.nh:
                hour_obj.nh.remove(h)
            elif h in hour_obj.ch:
                hour_obj.ch.remove(h)
                hour_obj.dyn_ch.pop(h)    
        return hour_obj

    def _get_average_price(self) -> float:
        if self.model.adjusted_average is not None:
            _affect_today = self.model.adjusted_average / stat.mean(self.model.prices_today)
            _affect_tomorrow = self.model.adjusted_average / stat.mean(self.model.prices_tomorrow)
        else:
            _affect_tomorrow = _affect_today = 1

        ret = self.model.prices_today[14::]
        ret[len(ret):] = self.model.prices_tomorrow[0:14]
        affected_ret= stat.mean(ret) * stat.mean([_affect_today, _affect_tomorrow])
        return affected_ret if self.model.adjusted_average is not None else min(stat.median(ret), stat.mean(ret))