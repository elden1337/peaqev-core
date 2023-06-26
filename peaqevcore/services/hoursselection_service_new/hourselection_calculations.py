from statistics import mean, stdev
import logging
from .models.hour_price import HourPrice

_LOGGER = logging.getLogger(__name__)


def normalize_prices(prices: list) -> list:
    min_price = min(prices)
    if min_price > 0:
        return prices
    c = 0
    if min_price <= 0:
        c = abs(min_price) + 0.01
    ret = []
    for p in prices:
        pp = p + c
        divider = min_price if min_price > 0 else c
        ret.append(round(pp - divider, 3))
    return ret


def block_nocturnal(
    hour_prices: list[HourPrice], block_nocturnal: bool = False
) -> None:
    if block_nocturnal:
        blockhours = [23, 0, 1, 2, 3, 4, 5, 6]
        for hp in hour_prices:
            if hp.hour in blockhours:
                hp.permittance = 0.0


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


def deviation_from_mean(prices: list[float]) -> dict[int, float]:
    if not len(prices):
        return {}
    avg = mean(prices)
    devi = stdev(prices)
    deviation_dict = {}
    for i, num in enumerate(prices):
        deviation = (num - avg) / devi
        if devi < 1:
            deviation *= 0.5
        deviation_dict[i] = round(deviation, 2)
    return deviation_dict


async def async_discard_excessive_hours(hours: dict):
    """There should always be at least four regular hours before absolute_top_price kicks in."""
    while len(hours) >= 20:
        to_pop = dict(sorted(hours.items(), key=lambda item: item[1]["val"]))
        hours.pop(list(to_pop.keys())[0])
    return hours
