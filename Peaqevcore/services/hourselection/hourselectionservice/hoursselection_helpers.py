import statistics as stat
from typing import Tuple
import logging
from ....models.hourselection.hourobject import HourObject
from ....models.hourselection.hourselectionmodels import HourSelectionModel

_LOGGER = logging.getLogger(__name__)

class HourSelectionInterimUpdate:
    @staticmethod
    def interim_avg_update(today: HourObject, tomorrow: HourObject, model: HourSelectionModel) -> Tuple[HourObject, HourObject, bool]:
        avg = HourSelectionInterimUpdate._get_average_price(model.prices_today, model.prices_tomorrow)
        _today = HourSelectionInterimUpdate._set_interim_per_day(
            True,
            avg, 
            model.prices_today, 
            today, 
            model.options.absolute_top_price, 
            model.options.min_price
            )
        _tomorrow = HourSelectionInterimUpdate._set_interim_per_day(
            False,
            avg, 
            model.prices_tomorrow, 
            tomorrow,  
            model.options.absolute_top_price, 
            model.options.min_price
            )

        conserve = True if _today[1] is True or _tomorrow[1] is True else False
        return _today[0], _tomorrow[0], conserve

    @staticmethod
    def _set_interim_per_day(
        is_today: bool,
        avg: float, 
        prices: list, 
        hour_obj: HourObject, 
        max_price: float = None, 
        min_price: float = None, 
        ) -> Tuple[HourObject, bool]:
        new_nonhours = []
        new_ok_hours = []
        _max_price = float('inf') if max_price is None else max_price
        _min_price = float('-inf') if min_price is None else min_price
        conserve_top_up = False

        for idx, p in enumerate(prices):
            if (idx >= 14 and is_today) or idx < 14:
                if p > avg or p > _max_price:
                    new_nonhours.append(idx)
                elif p <= avg or p <= _min_price:
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
        
        if len(new_nonhours) > 0 or len(new_ok_hours) > 0:
            conserve_top_up = True

        for h in new_ok_hours:
            if h in hour_obj.nh:
                hour_obj.nh.remove(h)
            elif h in hour_obj.ch:
                hour_obj.ch.remove(h)
                hour_obj.dyn_ch.pop(h)    
        print(hour_obj.nh)
        return HourObject(hour_obj.nh, hour_obj.ch, hour_obj.dyn_ch), conserve_top_up

    @staticmethod
    def _get_average_price(prices_today: list, prices_tomorrow:list) -> float:
        ret = prices_today[14::]
        ret[len(ret):] = prices_tomorrow[0:14]
        return stat.mean(ret)


class HourSelectionHelpers:
    @staticmethod
    def _create_dict(input: list):
        ret = {}
        for idx, val in enumerate(input):
            ret[idx] = val
        print(len(ret))
        if 23 <= len(ret) <= 24:
            return ret
        elif len(ret) == 25:
            _LOGGER.debug(f"Looks like we are heading into DST. re-parsing hours")
            input.pop(2)
            return HourSelectionHelpers._create_dict(input)
        else:
            _LOGGER.exception(f"Could not create dictionary from pricelist: {input} with len {len(ret)}.")
            raise ValueError
        

    @staticmethod
    def _try_parse(input:str, parsetype:type):
        try:
            ret = parsetype(input)
            return ret
        except:
            return False
    
    @staticmethod
    def _convert_none_list(lst: any) -> list:
        ret = []
        if lst is None or not isinstance(lst, list):
            return ret
        try:
            for l in lst:
                if l is None:
                    return ret
            return lst
        except:
            return HourSelectionHelpers._make_array_from_empty(lst)

    @staticmethod
    def _make_array_from_empty(input) -> list:
        array = input.split(",")
        list = [p for p in array if len(p) > 0]
        ret = []
        if len(list) > 24:
            try:
                for l in list:
                    parsed_item = HourSelectionHelpers._try_parse(l, float)
                    if not parsed_item:
                        parsed_item = HourSelectionHelpers._try_parse(l, int)
                    assert type(parsed_item) is float or type(parsed_item) is int
                    ret.append(parsed_item)
                return ret
            except:
                return []
        return []


class HourSelectionCalculations:
    @staticmethod
    def normalize_prices(prices:list) -> list:
        min_price = min(prices)
        c = 0
        if min_price <= 0:
            c = abs(min_price) + 0.01
        ret = []
        for p in prices:
            pp = p+c
            divider = min_price if min_price > 0 else c
            ret.append(pp/divider)
        return ret

    @staticmethod
    def rank_prices(hourdict: dict, normalized_hourdict: dict) -> dict:
        ret = {}
        _maxval = max(hourdict.values())
        _max_normalized = max(normalized_hourdict.values())
        peaqstdev = _maxval/abs(_max_normalized/stat.stdev(normalized_hourdict.values()))
        
        if peaqstdev < min(hourdict.values()):
            peaqstdev = peaqstdev + min(hourdict.values())
        for key in hourdict:
            if hourdict[key] > peaqstdev:
                _permax = round(hourdict[key] / _maxval, 2)
                ret[key] = {"val": hourdict[key], "permax": _permax}
        return HourSelectionCalculations._discard_excessive_hours(ret)

    @staticmethod
    def _discard_excessive_hours(hours: dict):
        """There should always be at least four regular hours before absolute_top_price kicks in."""
        while len(hours) >= 20:
            to_pop = dict(sorted(hours.items(), key=lambda item: item[1]['val']))    
            hours.pop(list(to_pop.keys())[0])
        return hours