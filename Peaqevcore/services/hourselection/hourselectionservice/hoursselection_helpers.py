import statistics as stat
import logging
from ....models.hourselection.hourobject import HourObject

_LOGGER = logging.getLogger(__name__)


class HourSelectionHelpers:
    
    @staticmethod
    def create_dict(input: list):
        ret = {}
        for idx, val in enumerate(input):
            ret[idx] = val
        if 23 <= len(ret) <= 24:
            return ret
        elif len(ret) == 25:
            _LOGGER.debug(f"Looks like we are heading into DST. re-parsing hours")
            input.pop(2)
            return HourSelectionHelpers.create_dict(input)
        else:
            _LOGGER.exception(f"Could not create dictionary from pricelist: {input} with len {len(ret)}.")
            raise ValueError

    @staticmethod
    def convert_none_list(lst: any) -> list:
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
    def _try_parse(input:str, parsetype:type):
        try:
            ret = parsetype(input)
            return ret
        except:
            return False

    @staticmethod
    def _make_array_from_empty(input: str) -> list:
        array = input.split(",")
        list = [p for p in array if len(p)]
        ret = []
        if len(list) > 24:
            try:
                for l in list:
                    parsed_item = HourSelectionHelpers._try_parse(l, float)
                    if not parsed_item:
                        parsed_item = HourSelectionHelpers._try_parse(l, int)
                    assert isinstance(parsed_item, (float,int))
                    ret.append(parsed_item)
                return ret
            except:
                _LOGGER.warning("Unable to create empty list for prices.")
                pass
        return []

    

    @staticmethod
    def _convert_collections(new: HourObject, index_deviation: int) -> HourObject:
        """Converts the hourobject-collections to interim days, based on the index-deviation provided."""

        def _chop_list(lst: list):
            return [n+index_deviation for n in lst if 0 <= n+index_deviation < 24]
        def _chop_dict(dct: dict):
            return {key+index_deviation:value for (key,value) in dct.items() if 0 <= key+index_deviation < 24}
        ret = HourObject([], [], {})
        ret.nh = _chop_list(new.nh)
        ret.ch = _chop_list(new.ch)
        ret.dyn_ch = _chop_dict(new.dyn_ch)
        ret.offset_dict = _chop_dict(new.offset_dict)
        ret.pricedict = _chop_dict(new.pricedict)
        return ret

    @staticmethod
    def _try_remove(value, collection: list|dict):
        if isinstance(collection, dict):
            if value in collection.keys():
                collection.pop(value)
        elif isinstance(collection, list):
            if value in collection:
                collection.remove(value)
        return collection


class HourSelectionCalculations:
    
    def normalize_prices(self, prices:list) -> list:
        min_price = min(prices)
        c = 0
        if min_price <= 0:
            c = abs(min_price) + 0.01
        ret = []
        for p in prices:
            pp = p+c
            divider = min_price if min_price > 0 else c
            ret.append(round(pp-divider,3))
        return ret

    def rank_prices(self, hourdict: dict, normalized_hourdict: dict, adjusted_average:float = None) -> dict:
        """Rank the normalized pricelist to find out which are going to become non- or caution-hours"""
        
        CAUTIONHOUR_CUTOFF = 0.7 #cutoff from the average to allow prices below average to become cautionary.

        _adj_avg = stat.mean(hourdict.values()) if not isinstance(adjusted_average, (float,int)) else adjusted_average
        adj_average_norm = _adj_avg * (stat.mean(normalized_hourdict.values())/stat.mean(hourdict.values()))
        cautions = [h for h in normalized_hourdict if normalized_hourdict[h] > (adj_average_norm * CAUTIONHOUR_CUTOFF)]
        maxval = max(hourdict.values())
        ret = {}
        
        for c in cautions:
            ret[c] = {"val": hourdict[c], "permax": round(hourdict[c] / maxval,2)}

        return self._discard_excessive_hours(ret)

    def _discard_excessive_hours(self, hours: dict):
        """There should always be at least four regular hours before absolute_top_price kicks in."""
        while len(hours) >= 20:
            to_pop = dict(sorted(hours.items(), key=lambda item: item[1]['val']))    
            hours.pop(list(to_pop.keys())[0])
        return hours