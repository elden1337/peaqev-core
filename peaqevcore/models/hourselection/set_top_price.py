import logging
from typing import Tuple
from .topprice_type import TopPriceType
from statistics import mean

_LOGGER = logging.getLogger(__name__)

def set_absolute_top_price(_min, _top) -> Tuple[float, TopPriceType, float]:
        if not validate_top_min_prices(_top, _min):
            _LOGGER.warning(f"Setting top-price and min-price to zero because of min-price being larger than top-price. Please fix in options. top:{_top} min:{_min}")
            _top = 0
            _min_price = 0
        else:
            _min_price = _min
        if _top is None:
            return float("inf"), TopPriceType.Unset, _min_price
        if _top <= 0:
            return float("inf"), TopPriceType.Unset, _min_price
        return float(_top), TopPriceType.Absolute, _min_price

def validate_top_min_prices(top, min) -> bool:
    if any(
        [top == 0, min == 0]
    ):  
        return True
    return top > min

async def async_validate_top_min_prices(top, min) -> bool:
        if any(
            [top == 0, min == 0]
        ):  
            return True
        return top > min

async def async_add_tomorrow(_day: int, prices_tomorrow: list, absolute_top_price: float) -> float:
        _current_sum = absolute_top_price * _day
        _current_sum += mean(prices_tomorrow)
        ret= _current_sum / (_day + 1)
        #print(absolute_top_price, ret)
        return ret