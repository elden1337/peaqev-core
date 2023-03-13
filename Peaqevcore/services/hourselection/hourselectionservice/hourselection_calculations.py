from statistics import mean
from ....models.hourselection.cautionhourtype import CautionHourType

def normalize_prices(prices:list) -> list:
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

def rank_prices(hourdict: dict, normalized_hourdict: dict, adjusted_average:float = None) -> dict:
    """Rank the normalized pricelist to find out which are going to become non- or caution-hours"""
    
    CAUTIONHOUR_CUTOFF = 0.7 #cutoff from the average to allow prices below average to become cautionary.

    _adj_avg = mean(hourdict.values()) if not isinstance(adjusted_average, (float,int)) else adjusted_average
    adj_average_norm = _adj_avg * (mean(normalized_hourdict.values())/mean(hourdict.values()))
    cautions = [h for h in normalized_hourdict if normalized_hourdict[h] > (adj_average_norm * CAUTIONHOUR_CUTOFF)]
    maxval = max(hourdict.values())
    ret = {}
    
    for c in cautions:
        ret[c] = {"val": hourdict[c], "permax": round(hourdict[c] / maxval,2)}

    return _discard_excessive_hours(ret)

def _discard_excessive_hours(hours: dict):
    """There should always be at least four regular hours before absolute_top_price kicks in."""
    while len(hours) >= 20:
        to_pop = dict(sorted(hours.items(), key=lambda item: item[1]['val']))    
        hours.pop(list(to_pop.keys())[0])
    return hours