import statistics as stat
import logging

_LOGGER = logging.getLogger(__name__)


class HourSelectionHelpers:
    @staticmethod
    def _create_dict(input: list):
        ret = {}
        for idx, val in enumerate(input):
            ret[idx] = val
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
    def _make_array_from_empty(input: str) -> list:
        array = input.split(",")
        list = [p for p in array if len(p) > 0]
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
    def rank_prices(hourdict: dict, normalized_hourdict: dict, adjusted_average:float = None) -> dict:
        _adj_avg = 1 if not isinstance(adjusted_average, float) else adjusted_average
        CAUTIONHOUR_CUTOFF = 1
        
        adj_average_norm = _adj_avg * (stat.mean(normalized_hourdict.values())/stat.mean(hourdict.values()))
        cautions = [h for h in normalized_hourdict if normalized_hourdict[h] > (adj_average_norm * CAUTIONHOUR_CUTOFF)]
        ret = {}
        
        maxval = max(hourdict.values())
        for c in cautions:
            ret[c] = {"val": hourdict[c], "permax": round(hourdict[c] / maxval,2)}

        return HourSelectionCalculations._discard_excessive_hours(ret)

    @staticmethod
    def get_offset_dict(normalized_hourdict: dict):
        ret = {}
        _prices = [p-min(normalized_hourdict.values()) for p in normalized_hourdict.values()]
        average_val = stat.mean(_prices)
        for i in range(0,24):
            try:
                ret[i] = round((_prices[i]/average_val) - 1,2)
            except:
                ret[i] = 1
        return ret

    @staticmethod
    def _discard_excessive_hours(hours: dict):
        """There should always be at least four regular hours before absolute_top_price kicks in."""
        while len(hours) >= 20:
            to_pop = dict(sorted(hours.items(), key=lambda item: item[1]['val']))    
            hours.pop(list(to_pop.keys())[0])
        return hours