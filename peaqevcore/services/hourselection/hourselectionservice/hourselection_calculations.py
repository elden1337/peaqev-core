from statistics import mean, stdev
import logging
from ....models.hourselection.cautionhourtype import CautionHourType, MAX_HOURS

_LOGGER = logging.getLogger(__name__)


def normalize_prices(prices: list) -> list:
    min_price = min(prices)
    c = 0
    if min_price <= 0:
        c = abs(min_price) + 0.01
    ret = []
    for p in prices:
        pp = p + c
        divider = min_price if min_price > 0 else c
        ret.append(round(pp - divider, 3))
    return ret


def get_offset_dict(normalized_hours: list):
    ret = {}
    _prices = [p - min(normalized_hours) for p in normalized_hours]
    average_val = mean(_prices)
    for i in range(0, len(_prices)):
        # todo: fix this to accommodate quarters also
        try:
            ret[i] = round((_prices[i] / average_val) - 1, 2)
        except:
            ret[i] = 1
    return ret

async def async_discard_excessive_hours(hours: dict):
    """There should always be at least four regular hours before absolute_top_price kicks in."""
    while len(hours) >= 20:
        to_pop = dict(sorted(hours.items(), key=lambda item: item[1]["val"]))
        hours.pop(list(to_pop.keys())[0])
    return hours


async def async_should_be_cautionhour(
    price_item, prices, peak, cautionhour_type
) -> bool:
    first = any(
        [
            float(price_item["permax"]) <= cautionhour_type,
            float(price_item["val"]) <= (sum(prices) / len(prices)),
        ]
    )
    second = (peak > 0 and peak * price_item["permax"] > 1) or peak == 0
    return all([first, second])


# async def async_set_charge_allowance(price_input, cautionhour_type) -> float:
#     return round(abs(price_input - 1), 2) * ALLOWANCE_SCHEMA[cautionhour_type]


# ALLOWANCE_SCHEMA = {
#     CautionHourType.get_num_value(CautionHourType.SUAVE): 1.15,
#     CautionHourType.get_num_value(CautionHourType.INTERMEDIATE): 1.05,
#     CautionHourType.get_num_value(CautionHourType.AGGRESSIVE): 1,
#     CautionHourType.get_num_value(CautionHourType.SCROOGE): 1,
# }
