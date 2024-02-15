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

def do_recalculate_prices(price_dict: dict, hours_prices: list[HourPrice], hdate: date) -> bool:
    if len(hours_prices) < 1:
        return True
    for d in price_dict.items():
        if d[0] not in [hp.dt for hp in hours_prices]:
            return True
    return False
    
# def do_recalculate_prices(price_dict: dict, hours_prices: list[HourPrice], hdate: date) -> bool:
#         if any([hp.dt.date() == hdate for hp in hours_prices]):
#         if [
#             hp.price
#             for hp in hours_prices
#             if hp.dt.date() == hdate
#         ] == prices and len(prices_tomorrow) < 1:
#             print("prices are the same as the previous day, so we will not recalculate")
#             """We should not recalculate prices if they are the same as the previous day"""
#             return False
#         return True


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