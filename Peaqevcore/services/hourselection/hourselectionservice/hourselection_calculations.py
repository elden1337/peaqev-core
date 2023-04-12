from statistics import mean
import logging
from ....models.hourselection.cautionhourtype import CautionHourType, MAX_HOURS

_LOGGER = logging.getLogger(__name__)


async def async_normalize_prices(prices:list) -> list:
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

async def async_get_offset_dict(normalized_hourdict: dict):
        ret = {}
        _prices = [p-min(normalized_hourdict.values()) for p in normalized_hourdict.values()]
        average_val = mean(_prices)
        for i in range(0,len(_prices)):
            try:
                ret[i] = round((_prices[i]/average_val) - 1,2)
            except:
                ret[i] = 1
        return ret

async def async_create_cautions(
        hourdict: dict, 
        normalized_hourdict: dict, 
        cautionhour_type: CautionHourType, 
        range_start: int = 0,
        adjusted_average:float|None = None, 
        blocknocturnal:bool = False
        ) -> dict:
    """Rank the normalized pricelist to find out which are going to become non- or caution-hours"""
    
    _adj_avg = adjusted_average
    if not isinstance(adjusted_average, (float,int)):
        _adj_avg = mean(hourdict.values()) 

    adj_average_norm = _adj_avg * (mean(normalized_hourdict.values())/mean(hourdict.values()))
    cautions = [h for h in normalized_hourdict if normalized_hourdict[h] > (adj_average_norm * 0.7)]
    cautions_dict = await async_cap_pricelist_available_hours(cautions, normalized_hourdict, cautionhour_type, blocknocturnal, range_start)
    maxval = max(hourdict.values())
    ret = {}
    
    try:
        for k, v in cautions_dict.items():
            ret[k] = {
                "val": hourdict[k], 
                "permax": round(hourdict[k] / maxval,2), 
                "force_non": v
                }
    except IndexError as e:
        _LOGGER.error(f"Error on creating the cautions_dict: {e}")

    if blocknocturnal:
        return ret
    else:
        return await async_discard_excessive_hours(ret)

async def async_cap_pricelist_available_hours(cautions: list, normalized_hourdict:dict, cautionhour_type: CautionHourType, blocknocturnal:bool, range_start: int) -> dict:
    _demand = max(len(normalized_hourdict.keys()) - MAX_HOURS.get(cautionhour_type),0)
    ret = {c: False for c in cautions} if _demand == 0 else {c: True for c in cautions}
    hours_sorted = [k for k, v in sorted(normalized_hourdict.items(), key=lambda item: item[1])]
    iterations = 0
    while len(cautions) < _demand and iterations < len(hours_sorted)*2:
        iterations+=1
        idx = max(range_start-1,0)
        if len(cautions) > 0:
            idx = hours_sorted.index(cautions[-1])
        
        if idx <= len(hours_sorted) -1:
            try:
                while idx+1 < len(hours_sorted):
                    idx += 1
                    next = hours_sorted[idx]
                    if next not in cautions:
                        cautions.append(next)
                        ret[next] = True
                        break
            except IndexError as e:
                raise IndexError(f"error on first. idx:{idx}")
        if idx >= 0:
            try:
                while idx-1 >= 0:
                    idx -= 1
                    prev = hours_sorted[idx]
                    if prev not in cautions:
                        cautions.append(prev)
                        ret[prev] = True
                        break
            except IndexError as e:
                raise IndexError(f"error on second. idx:{idx}")

    try:
        for i in await async_get_nocturnal_stop(blocknocturnal, range_start):
            if i not in cautions:
                ret[i] = True
    except IndexError as e:
        _LOGGER.error(f"error on looping nocturnal stop: {e}")
    return await async_sort_by_key(ret)

async def async_sort_by_key(input: dict) -> dict:
    _keys = list(input.keys())
    _keys.sort()
    return {i: input[i] for i in _keys}

async def async_get_nocturnal_stop(blocknocturnal: bool = False, range_start: int = 0) -> list:
    _base = [23,0,1,2,3,4,5,6]
    if blocknocturnal:
        return await async_transform_range(range_start, _base)
    return []


async def async_transform_range(range_start, base):
    if range_start == 0:
            return base
    ret = []
    for b in base:
        if b >= range_start:
            ret.append(b-range_start)
        else:
            ret.append(24-range_start+b)
    return ret


async def async_discard_excessive_hours(hours: dict):
    """There should always be at least four regular hours before absolute_top_price kicks in."""
    while len(hours) >= 20:
        to_pop = dict(sorted(hours.items(), key=lambda item: item[1]['val']))    
        hours.pop(list(to_pop.keys())[0])
    return hours


async def async_should_be_cautionhour(price_item, prices, peak, cautionhour_type) -> bool:
    first = any([
                float(price_item["permax"]) <= cautionhour_type,
                float(price_item["val"]) <= (sum(prices)/len(prices))
            ])
    second = (peak > 0 and peak*price_item["permax"] > 1) or peak == 0
    return all([first, second])


async def async_set_charge_allowance(price_input, cautionhour_type) -> float:
    return round(abs(price_input - 1), 2) * ALLOWANCE_SCHEMA[cautionhour_type]

ALLOWANCE_SCHEMA = {
    CautionHourType.get_num_value(CautionHourType.SUAVE): 1.15,
    CautionHourType.get_num_value(CautionHourType.INTERMEDIATE): 1.05,
    CautionHourType.get_num_value(CautionHourType.AGGRESSIVE): 1,
    CautionHourType.get_num_value(CautionHourType.SCROOGE): 1
}