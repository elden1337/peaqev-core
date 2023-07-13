from statistics import mean, stdev
import logging
from .models.hour_price import HourPrice
from datetime import date

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


def do_recalculate_prices(prices: list[float], prices_tomorrow: list[float]|None, hours_prices: list[HourPrice], hdate: date) -> bool:
        if [
            hp.price
            for hp in hours_prices
            if hp.dt.date() == hdate
        ] == prices and len(prices_tomorrow) < 1:
            return False
        return True


def get_average_kwh_price(future_hours: list[HourPrice]) -> float:
        try:
            return mean(
                [
                    hp.price
                    for hp in future_hours
                    if hp.permittance > 0
                ]
            )
        except Exception:
            return 0.0