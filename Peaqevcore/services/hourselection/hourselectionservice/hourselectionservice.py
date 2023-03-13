import logging
from datetime import datetime
from typing import Tuple
import statistics as stat
from ....models.hourselection.cautionhourtype import CautionHourType, MAX_HOURS
from .hoursselection_helpers import convert_collections, try_remove, create_dict
from .hourselection_calculations import normalize_prices, rank_prices, get_offset_dict
from ....models.hourselection.hourobject import HourObject
from ....models.hourselection.hourselectionmodels import HourSelectionModel
from ....models.hourselection.hourtypelist import HourTypeList

_LOGGER = logging.getLogger(__name__)

ALLOWANCE_SCHEMA = {
    CautionHourType.get_num_value(CautionHourType.SUAVE): 1.15,
    CautionHourType.get_num_value(CautionHourType.INTERMEDIATE): 1.05,
    CautionHourType.get_num_value(CautionHourType.AGGRESSIVE): 1,
    CautionHourType.get_num_value(CautionHourType.SCROOGE): 1
}

class HourSelectionService:
    def __init__(self, parent, base_mock_hour: int = None):
        self.parent = parent
        self._mock_hour = base_mock_hour
        self._preserve_interim: bool = False

    def update(self, caller: str = None) -> None:
        if self._preserve_interim and caller == "today":
            self.parent.model.hours.hours_today = self.parent.model.hours.hours_tomorrow
            self.parent.model.hours.hours_tomorrow = HourObject([], [], {})
            return

        hours, hours_tomorrow = self._interim_day_update(
            today=self._update_per_day(prices=self.parent.model.prices_today), 
            tomorrow=self._update_per_day(prices=self.parent.model.prices_tomorrow)
            )
        self.parent.model.hours.hours_today = self._add_remove_limited_hours(hours)
        self.parent.model.hours.hours_tomorrow = self._add_remove_limited_hours(hours_tomorrow)
        self.update_hour_lists()

    def _update_per_day(self, prices: list) -> HourObject:
        pricedict = {}
        if prices is not None and len(prices) > 1:
            pricedict = create_dict(prices)
            normalized_pricedict = create_dict(
                normalize_prices(prices)
                )
            if stat.stdev(prices) > 0.05:
                ready_hours = self._determine_hours(
                    rank_prices(
                        pricedict, 
                        normalized_pricedict,
                        self.parent.cautionhour_type_enum,
                        self.parent.model.adjusted_average
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
            ret.offset_dict=get_offset_dict(normalized_pricedict)
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
                    self.parent.model.hours.update_non_hours(hour)
                case HourTypeList.CautionHour:
                    self.parent.model.hours.update_caution_hours(hour)
                case HourTypeList.DynCautionHour:
                    self.parent.model.hours.update_dynanmic_caution_hours(hour)   
                case _:
                    pass
        else:
            self.parent.model.hours.update_non_hours(hour)
            self.parent.model.hours.update_caution_hours(hour)
            self.parent.model.hours.update_dynanmic_caution_hours(hour)
            self.parent.model.hours.update_offset_dict()

    def _add_remove_limited_hours(self, hours: HourObject) -> HourObject:
        """Removes cheap hours and adds expensive hours set by user limitation"""
        if hours is None or all(
            [
                len(hours.nh) == 0, 
                len(hours.ch) == 0, 
                len(hours.dyn_ch) == 0
            ]):
            return HourObject(
                offset_dict=hours.offset_dict,
                pricedict=hours.pricedict
                )
        hours.add_expensive_hours(self.parent.model.options.absolute_top_price)
        hours.remove_cheap_hours(self.parent.model.options.min_price)
        
        return hours

    def _determine_hours(self, price_list: dict, prices: list) -> HourObject:
        ret = HourObject([],[],{})
        for p in price_list:
            _permax = self.__set_charge_allowance(price_list[p]["permax"])
            if self.__should_be_cautionhour(price_list[p], prices):
                ret.ch.append(p)
                ret.dyn_ch[p] = round(_permax,2)
            else:
                ret.nh.append(p)
        return ret

    def __should_be_cautionhour(self, price_item, prices) -> bool:
        first = any([
                    float(price_item["permax"]) <= self.parent.model.options.cautionhour_type,
                    float(price_item["val"]) <= (sum(prices)/len(prices))
                ])
        _peak = self.parent.model.current_peak
        second = (_peak > 0 and _peak*price_item["permax"] > 1) or _peak == 0
        return all([first, second])

    def __set_charge_allowance(self, price_input) -> float:
        return round(abs(price_input - 1), 2) * ALLOWANCE_SCHEMA[self.parent.model.options.cautionhour_type]
        
    def set_hour(self, testhour:int = None) -> int:
        return testhour if testhour is not None else self._mock_hour if self._mock_hour is not None else datetime.now().hour

    def _interim_day_update(self, today: HourObject, tomorrow: HourObject) -> Tuple[HourObject, HourObject]:
        """Updates the non- and caution-hours with an adjusted mean of 14h - 13h today-tomorrow to get a more sane nightly curve."""

        if len(self.parent.model.prices_tomorrow) < 23:
            return today, tomorrow 
        
        #hour = self._mock_hour if self._mock_hour is not None else 14
        hour =14
        negative_hour = (24 - hour)*-1

        pricelist = self.parent.model.prices_today[hour::]
        pricelist[len(pricelist):] = self.parent.model.prices_tomorrow[0:hour]
        new_hours = self._update_per_day(pricelist)
        
        today = self._update_interim_lists(range(hour,24), today, new_hours, hour)
        tomorrow = self._update_interim_lists(range(0,hour), tomorrow, new_hours, negative_hour)

        self._preserve_interim = True
        return today, tomorrow

    def _update_interim_lists(self, _range: range, old: HourObject, new: HourObject, index_devidation: int) -> HourObject:
        _new = convert_collections(new, index_devidation)
        for i in _range:
            if i in _new.nh:
                if i not in old.nh:
                    old.nh.append(i)
                    old.ch = try_remove(i, old.ch)
                    old.dyn_ch = try_remove(i, old.dyn_ch)
            elif i in _new.ch:
                if i not in old.ch:
                    old.ch.append(i)
                    old.dyn_ch[i] = _new.dyn_ch[i]
                    old.nh = try_remove(i, old.nh)
            else:
                old.nh = try_remove(i, old.nh)
                old.ch = try_remove(i, old.ch)
                old.dyn_ch = try_remove(i, old.dyn_ch)
            old.nh.sort()
            old.ch.sort()
            old.dyn_ch = dict(sorted(old.dyn_ch.items()))
        
        for r in _new.offset_dict.keys():
            old.offset_dict[r] = _new.offset_dict[r]
            old.pricedict[r] = _new.pricedict[r]
        return old

    

    
