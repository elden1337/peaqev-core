import pytest
import statistics as stat
from ..services.hourselection.hoursselection import Hoursselection as h
from ..models.hourselection.cautionhourtype import CautionHourType

def test_summertime_tomorrow():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE, absolute_top_price=3, min_price=0.0)
    prices = [0.505, 0.517, 0.544, 0.558, 0.588, 0.613, 0.637, 0.689, 0.84, 1.067, 1.014, 0.939, 0.77, 0.63, 0.699, 0.77, 1.106, 1.383, 1.399, 0.749, 0.469, 0.442, 0.396, 0.349]
    prices_tomorrow = [0.363, 0.361, 0.369, 0.469, 0.546, 0.574, 1.445, 1.461, 1.45, 1.446, 1.419, 1.355, 1.333, 1.333, 1.355, 1.393, 1.467, 1.523, 1.684, 1.512, 1.498, 1.448, 1.107]
    r.update_prices(prices, prices_tomorrow)
    r.service._mock_hour = 14
    assert r.non_hours == [16, 17, 18, 6, 7, 8, 9, 10, 11, 12, 13]
    assert len(r.prices_tomorrow) == 23

def test_summertime_today():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE, absolute_top_price=3, min_price=0.0)
    prices = [0.505, 0.517, 0.544, 0.588, 0.613, 0.637, 0.689, 0.84, 1.067, 1.014, 0.939, 0.77, 0.63, 0.699, 0.77, 1.106, 1.383, 1.399, 0.749, 0.469, 0.442, 0.396, 0.349]
    prices_tomorrow = [0.363, 0.361, 0.369, 0.402, 0.469, 0.546, 0.574, 1.445, 1.461, 1.45, 1.446, 1.419, 1.355, 1.333, 1.333, 1.355, 1.393, 1.467, 1.523, 1.684, 1.512, 1.498, 1.448, 1.107]
    r.update_prices(prices, prices_tomorrow)
    r.service._mock_hour = 14
    assert r.non_hours == [15, 16, 17, 7, 8, 9, 10, 11, 12, 13]
    assert len(r.prices) == 23

def test_wintertime_tomorrow():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE, absolute_top_price=3, min_price=0.0)
    prices = [0.505, 0.517, 0.544, 0.558, 0.588, 0.613, 0.637, 0.689, 0.84, 1.067, 1.014, 0.939, 0.77, 0.63, 0.699, 0.77, 1.106, 1.383, 1.399, 0.749, 0.469, 0.442, 0.396, 0.349]
    prices_tomorrow = [0.363, 0.361, 0.369, 1, 0.402, 0.469, 0.546, 0.574, 1.445, 1.461, 1.45, 1.446, 1.419, 1.355, 1.333, 1.333, 1.355, 1.393, 1.467, 1.523, 1.684, 1.512, 1.498, 1.448, 1.107]
    r.update_prices(prices, prices_tomorrow)
    r.service._mock_hour = 14
    assert r.non_hours == [16, 17, 18, 2, 7, 8, 9, 10, 11, 12, 13]
    assert len(r.prices_tomorrow) == 24

def test_wintertime_today():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE, absolute_top_price=3, min_price=0.0)
    prices = [0.505, 0.517, 0.544, 1, 0.558, 0.588, 0.613, 0.637, 0.689, 0.84, 1.067, 1.014, 0.939, 0.77, 0.63, 0.699, 0.77, 1.106, 1.383, 1.399, 0.749, 0.469, 0.442, 0.396, 0.349]
    prices_tomorrow = [0.363, 0.361, 0.369, 0.402, 0.469, 0.546, 0.574, 1.445, 1.461, 1.45, 1.446, 1.419, 1.355, 1.333, 1.333, 1.355, 1.393, 1.467, 1.523, 1.684, 1.512, 1.498, 1.448, 1.107]
    r.update_prices(prices, prices_tomorrow)
    r.service._mock_hour = 14
    assert r.non_hours == [16, 17, 18, 7, 8, 9, 10, 11, 12, 13]
    assert len(r.prices) == 24





