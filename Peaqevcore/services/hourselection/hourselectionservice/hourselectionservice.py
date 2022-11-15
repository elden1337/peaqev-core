import logging
from datetime import datetime
import statistics as stat
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
        adjusted_average:float = None
        ):
        hours_ready = self._update_per_day(prices=self.model.prices_today, adjusted_average=adjusted_average)
        hours = self._add_remove_limited_hours(hours_ready)
        hours_tomorrow = HourObject([],[],dict())
        if self.model.prices_tomorrow is not None and len(self.model.prices_tomorrow) > 0:
            tomorrow_ready = self._update_per_day(self.model.prices_tomorrow)
            hours_tomorrow = self._add_remove_limited_hours(tomorrow_ready)
            hours, hours_tomorrow = interim.interim_avg_update(
                today=hours, 
                tomorrow=hours_tomorrow, 
                model =self.model
                )
            
            self.model.hours.hours_today = self._add_remove_limited_hours(
                HourObjectExtended(hours.nh, hours.ch, hours.dyn_ch, hours_ready.pricedict)
                )
            self.model.hours.hours_tomorrow = self._add_remove_limited_hours(
                HourObjectExtended(hours_tomorrow.nh, hours_tomorrow.ch, hours_tomorrow.dyn_ch, tomorrow_ready.pricedict)
            )
        else:
            self.model.hours.hours_today = hours
            self.model.hours.hours_tomorrow = hours_tomorrow
        self.update_hour_lists()
 
    def _update_per_day(self, prices: list, adjusted_average:float = None) -> HourObjectExtended:
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
                        adjusted_average
                        ), 
                        prices
                        )
                return HourObjectExtended(
                    ready_hours.nh, 
                    ready_hours.ch, 
                    ready_hours.dyn_ch, 
                    pricedict
                    )
            return HourObjectExtended([], [], dict(), pricedict)

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

    def _add_remove_limited_hours(self, hours: HourObjectExtended) -> HourObject:
        """Removes cheap hours and adds expensive hours set by user limitation"""
        if hours is None:
            return HourObject([],[],dict())
        if self.model.options.absolute_top_price is not None:
                ret = hours.add_expensive_hours(self.model.options.absolute_top_price)
        else: 
            ret = HourObject(hours.nh, hours.ch, hours.dyn_ch)
        if self.model.options.min_price > 0:
            ret = hours.remove_cheap_hours(self.model.options.min_price)
        return ret

    def _determine_hours(self, price_list: dict, prices: list) -> HourObject:
        _nh = []
        _dyn_ch = {}
        _ch = []
        for p in price_list:
            _permax = self._set_permax(price_list[p]["permax"])
            if any([
                float(price_list[p]["permax"]) <= self.model.options.cautionhour_type,
                float(price_list[p]["val"]) <= (sum(prices)/len(prices))
            ]):
                _ch.append(p)
                _dyn_ch[p] = round(_permax,2)
            else:
                _nh.append(p)
        return HourObject(_nh, _ch, _dyn_ch)

    def _set_permax(self, price_input) -> float:
        _permax = round(abs(price_input - 1), 2)
        if self.model.options.cautionhour_type == CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE]:
            _permax += 0.15
        elif self.model.options.cautionhour_type == CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE]:
            _permax += 0.05
        return _permax

    def set_hour(self, testhour:int = None) -> int:
        return testhour if testhour is not None else self._base_mock_hour if self._base_mock_hour is not None else datetime.now().hour
