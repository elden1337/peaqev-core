import logging
from datetime import datetime
from typing import Tuple
import statistics as stat

from .hoursselection_helpers import create_dict
from .hourselection_calculations import normalize_prices, create_cautions, get_offset_dict, should_be_cautionhour, set_charge_allowance
from ....models.hourselection.hourobjects.hourobject import HourObject
from ....models.hourselection.hourobjects.hourobject_helpers import update_interim_lists
from ....models.hourselection.hourselectionmodels import HourSelectionModel

from ....models.hourselection.hourtypelist import HourTypeList

_LOGGER = logging.getLogger(__name__)


class HourSelectionService:
    def __init__(self, parent, base_mock_hour: int = None):
        self.parent = parent
        self._mock_hour = base_mock_hour
        self.preserve_interim: bool = False
        self._midnight_touched: bool = False

    def update(self) -> None:
        if all([len(self.parent.model.prices_today) == 0, len(self.parent.model.prices_tomorrow) == 0]):
            return
        if self.preserve_interim: 
            self._change_midnight_data()  
        else:
            self._midnight_touched = False
            today=self._update_per_day(prices=self.parent.model.prices_today)
            tomorrow=self._update_per_day(prices=self.parent.model.prices_tomorrow)
            hours, hours_tomorrow = self._interim_day_update(today, tomorrow)

            self.parent.model.hours.hours_today = self._add_remove_limited_hours(hours)
            self.parent.model.hours.hours_tomorrow = self._add_remove_limited_hours(hours_tomorrow)
            self.parent.model.hours.update_hour_lists(hour=self.set_hour())

    def _change_midnight_data(self) -> None:        
        if self.parent.model.prices_tomorrow == []:
            if not self._midnight_touched:
                self.parent.model.hours.hours_today = self.parent.model.hours.hours_tomorrow
                self.parent.model.hours.hours_tomorrow = HourObject([], [], {})
                self.parent.model.hours.offset_dict["today"] = self.parent.model.hours.offset_dict.get("tomorrow", {})
                self.parent.model.hours.offset_dict["tomorrow"] = {}
                self._midnight_touched = True
        else:
            self.preserve_interim = False
            self.update()

    def _update_per_day(self, prices: list, range_start: int =0) -> HourObject:
        pricedict = {}
        if prices is not None and len(prices) > 1:
            pricedict = create_dict(prices)
            normalized_pricedict = create_dict(
                normalize_prices(prices)
                )
            if stat.stdev(prices) > 0.05:
                ranked = create_cautions(
                        pricedict, 
                        normalized_pricedict,
                        self.parent.cautionhour_type_enum,
                        range_start,
                        self.parent.model.adjusted_average,
                        self.parent.model.options.blocknocturnal
                        )
                ready_hours = self._determine_hours(ranked, prices)
                ret= HourObject(
                    nh=ready_hours.nh, 
                    ch=ready_hours.ch, 
                    dyn_ch=ready_hours.dyn_ch, 
                    pricedict=pricedict
                    )
            else:
                """the price curve is too flat to determine hours"""
                ret= HourObject(nh=[], ch=[], dyn_ch={},pricedict=pricedict)
            ret.offset_dict=get_offset_dict(normalized_pricedict)
            return ret
        return HourObject([],[],{})

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
        ch_type = self.parent.model.options.cautionhour_type
        peak = self.parent.model.current_peak
        try:
            for p in price_list:    
                if price_list[p]["force_non"] is True:
                    ret.nh.append(p)
                elif should_be_cautionhour(price_list[p], prices, peak, ch_type):
                    ret.ch.append(p)
                    ret.dyn_ch[p] = round(set_charge_allowance(price_list[p]["permax"], ch_type),2)
                else:
                    ret.nh.append(p)
        except IndexError as e:
            _LOGGER.error(f"Error in determine hours: {e}")
        return ret
    
    def set_hour(self, testhour:int = None) -> int:
        return testhour if testhour is not None else self._mock_hour if self._mock_hour is not None else datetime.now().hour

    def _interim_day_update(self, today: HourObject, tomorrow: HourObject) -> Tuple[HourObject, HourObject]:
        """Updates the non- and caution-hours with an adjusted mean of 14h - 13h today-tomorrow to get a more sane nightly curve."""
        if len(self.parent.model.prices_tomorrow) < 23:
            self.preserve_interim = False
            return today, tomorrow 
        
        hour =len(self.parent.prices)-10
        negative_hour = (len(self.parent.prices) - hour)*-1
        pricelist = self.parent.model.prices_today[hour::]
        pricelist[len(pricelist):] = self.parent.model.prices_tomorrow[0:hour]
        new_hours = self._update_per_day(pricelist, hour)
        
        today = update_interim_lists(range(hour,len(self.parent.prices)), today, new_hours, hour)
        tomorrow = update_interim_lists(range(0,hour), tomorrow, new_hours, negative_hour)
        self.preserve_interim = True
        return today, tomorrow
