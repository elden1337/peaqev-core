from datetime import datetime
import statistics as stat
from .top_up import top_up, TopUpDTO
from ...models.hourselection.const import (
    CAUTIONHOURTYPE_SUAVE,
    CAUTIONHOURTYPE_INTERMEDIATE,
    CAUTIONHOURTYPE
)
from enum import Enum
from .hoursselection_helpers import HourSelectionHelpers
from ...models.hourselection.hourobject import HourObject, HourObjectExtended
from ...models.hourselection.hourselectionmodels import HourSelectionModel, HourSelectionOptions

class HourTypeList(Enum):
    NonHour = 0
    CautionHour = 1
    DynCautionHour = 2


class Hoursselection:
    def __init__(
            self,      
            absolute_top_price: float = 0,
            min_price: float = 0,
            cautionhour_type: float = CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE],
            allow_top_up: bool = False,
            base_mock_hour: int = None
    ):
        self.model = HourSelectionModel(
            options=HourSelectionOptions(
                cautionhour_type=cautionhour_type, 
                absolute_top_price=self._set_absolute_top_price(absolute_top_price), 
                min_price=min_price, 
                allow_top_up=allow_top_up
                )
            )
        self._base_mock_hour: int = base_mock_hour
        self._validate()
    
    def _set_absolute_top_price(self, val) -> float:
        if val is None:
            return float("inf")
        if val <= 0:
            return float("inf")
        return float(val)

    def _validate(self):
        assert 0 < self.model.options.cautionhour_type <= 1

    @property
    def options(self) -> HourSelectionOptions:
        return self.model.options

    @property
    def non_hours(self) -> list:
        self._update_hour_lists(self.model.hours.hours_today, self.model.hours.hours_tomorrow, listtype=HourTypeList.NonHour)
        return self.model.hours.non_hours

    @property
    def caution_hours(self) -> list:
        self._update_hour_lists(self.model.hours.hours_today, self.model.hours.hours_tomorrow, listtype=HourTypeList.CautionHour)
        return self.model.hours.caution_hours

    @property
    def dynamic_caution_hours(self) -> dict:
        self._update_hour_lists(self.model.hours.hours_today, self.model.hours.hours_tomorrow, listtype=HourTypeList.DynCautionHour)
        return self.model.hours.dynamic_caution_hours

    @property
    def prices(self) -> list:
        return self.model.prices_today

    @prices.setter
    def prices(self, val):
        self.model.prices_today = val
        if self.prices == self.prices_tomorrow:
            self.prices_tomorrow = None
        else:
            self.update()

    @property
    def prices_tomorrow(self) -> list:
        return self.model.prices_tomorrow

    @prices_tomorrow.setter
    def prices_tomorrow(self, val):
        self.model.prices_tomorrow = HourSelectionHelpers._convert_none_list(val)
        self.update()

    def update(self, testhour:int = None):
        if testhour is not None:
            self._base_mock_hour = testhour
        today_ready = self._update_per_day(self.prices)
        hours_today = self._add_remove_limited_hours(today_ready)
        hours_tomorrow = HourObject([],[],dict())
        
        if self.prices_tomorrow is not None and len(self.prices_tomorrow) > 0:
            self.options.conserve_top_up = False
            hours_tomorrow = self._add_remove_limited_hours(
                self._update_per_day(self.prices_tomorrow)
                )

        self.model.hours.hours_today = hours_today
        self.model.hours.hours_tomorrow = hours_tomorrow
        self._update_hour_lists(hours_today=hours_today, hours_tomorrow=hours_tomorrow, testhour=testhour)
        
    def _set_top_up(self, testhour: int = None) -> None:
        if self.model.options.allow_top_up is True and self.prices_tomorrow is not None and len(self.prices_tomorrow) > 0:
            ret = top_up(TopUpDTO(
                self.model.hours.non_hours, 
                self.model.hours.caution_hours, 
                self.model.hours.dynamic_caution_hours, 
                self.model.options.absolute_top_price,
                self.model.options.min_price,
                testhour if testhour is not None else self._base_mock_hour if self._base_mock_hour is not None else datetime.now().hour, 
                self.model.hours.hours_today, 
                self.model.hours.hours_tomorrow, 
                self.model.prices_today, 
                self.model.prices_tomorrow
                ))
            if ret.nh != self.model.hours.non_hours:
                self.model.options.conserve_top_up = True
                self.model.hours.non_hours = ret.nh
                self.model.hours.caution_hours = ret.ch
                self.model.hours.dynamic_caution_hours = ret.dyn_ch

    def _update_hour_lists(self, hours_today:HourObject, hours_tomorrow:HourObject, testhour:int = None, listtype:HourTypeList = None) -> None:
        hour = testhour if testhour is not None else self._base_mock_hour if self._base_mock_hour is not None else datetime.now().hour
        if self.options.conserve_top_up is False:
            if listtype is not None:
                match listtype:
                    case HourTypeList.NonHour:
                        self._update_nonhour_list(hours_today, hours_tomorrow, hour)
                    case HourTypeList.CautionHour:
                        self._update_cautionhour_list(hours_today, hours_tomorrow, hour)
                    case HourTypeList.DynCautionHour:
                        self._update_dyn_cautionhour_dict(hours_today, hours_tomorrow, hour)
                    case _:
                        pass
                self._set_top_up(hour)
            else:
                self._update_nonhour_list(hours_today, hours_tomorrow, hour)
                self._update_cautionhour_list(hours_today, hours_tomorrow, hour)
                self._update_dyn_cautionhour_dict(hours_today, hours_tomorrow, hour)
        
    def _update_nonhour_list(self, hours_today:HourObject, hours_tomorrow:HourObject, hour:int) -> None:
        self.model.hours.non_hours = []
        self.model.hours.non_hours.extend(h for h in hours_today.nh if h >= hour)
        self.model.hours.non_hours.extend(h for h in hours_tomorrow.nh if h < hour)

    def _update_cautionhour_list(self, hours_today:HourObject, hours_tomorrow:HourObject, hour:int) -> None:
        self.model.hours.caution_hours = []
        self.model.hours.caution_hours.extend(h for h in hours_today.ch if h >= hour)
        self.model.hours.caution_hours.extend(h for h in hours_tomorrow.ch if h < hour)

    def _update_dyn_cautionhour_dict(self, hours_today:HourObject, hours_tomorrow:HourObject, hour:int) -> None:
        self.model.hours.dynamic_caution_hours = dict()
        self.model.hours.dynamic_caution_hours.update({k: v for k, v in hours_today.dyn_ch.items() if k >= hour})
        self.model.hours.dynamic_caution_hours.update({k: v for k, v in hours_tomorrow.dyn_ch.items() if k < hour})

    def _update_per_day(self, prices) -> HourObjectExtended:
        pricedict = dict
        if prices is not None and len(prices) > 1:
            pricedict = HourSelectionHelpers._create_dict(prices)
            normalized_pricedict = HourSelectionHelpers._create_dict(
                HourSelectionHelpers._normalize_prices(prices)
                )
            if stat.stdev(prices) > 0.05:
                prices_ranked = HourSelectionHelpers._rank_prices(pricedict, normalized_pricedict)
                ready_hours = self._determine_hours(prices_ranked, prices)
                return HourObjectExtended(
                    ready_hours.nh, 
                    ready_hours.ch, 
                    ready_hours.dyn_ch, 
                    pricedict
                    )
            return HourObjectExtended([], [], dict(), pricedict)
        
    def _add_remove_limited_hours(self, hours: HourObjectExtended) -> HourObject:
        """Removes cheap hours and adds expensive hours set by user limitation"""
        if hours is None:
            return HourObject([],[],dict())

        if self.model.options.absolute_top_price is not None:
                ret = self._add_expensive_non_hours(hours)
        else: 
            ret = HourObject(hours.nh, hours.ch, hours.dyn_ch)
        if self.model.options.min_price > 0:
            ret = self._remove_cheap_hours(hours)
        return ret

    def _remove_cheap_hours(self, hours: HourObjectExtended) -> HourObject:
        lst = (h for h in hours.pricedict if hours.pricedict[h] < self.model.options.min_price)
        for h in lst:
            if h in hours.nh:
                hours.nh.remove(h)
            elif h in hours.ch:
                hours.ch.remove(h)
                hours.dyn_ch.pop(h)    
        return HourObject(hours.nh, hours.ch, hours.dyn_ch)

    def _add_expensive_non_hours(self, readyhours:HourObjectExtended) -> HourObject:
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
    
    def get_average_kwh_price(self, testhour:int = None):
        ret = self._get_charge_or_price(testhour=testhour)
        return round(sum(ret.values())/len(ret),2)
        
    def get_total_charge(self, currentpeak:float, testhour:int = None) -> float:
        ret = self._get_charge_or_price(currentpeak, testhour)
        return round(sum(ret.values()),1)

    def _get_charge_or_price(self, currentpeak:float = None, testhour:int = None) -> dict:
        hour = self._set_hour(testhour)
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

        if self.prices_tomorrow is None:
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

    def _set_hour(self, testhour:int = None) -> int:
        return datetime.now().hour if testhour is None else testhour

