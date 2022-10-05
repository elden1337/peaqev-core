import pytest
from ..services.hourselection.hoursselection import Hoursselection as h
from ..services.hourselection.hourselectionservice.hoursselection_helpers import HourSelectionHelpers, HourSelectionCalculations
from ..models.hourselection.const import (CAUTIONHOURTYPE_AGGRESSIVE, CAUTIONHOURTYPE_INTERMEDIATE, CAUTIONHOURTYPE_SUAVE, CAUTIONHOURTYPE)

MOCKPRICES1 =[0.129, 0.123, 0.077, 0.064, 0.149, 0.172, 1, 2.572, 2.688, 2.677, 2.648, 2.571, 2.561, 2.07, 2.083, 2.459, 2.508, 2.589, 2.647, 2.648, 2.603, 2.588, 1.424, 0.595]
MOCKPRICES2 =[0.392, 0.408, 0.418, 0.434, 0.408, 0.421, 0.45, 0.843, 0.904, 1.013, 0.939, 0.915, 0.703, 0.445, 0.439, 0.566, 0.913, 1.4, 2.068, 2.182, 1.541, 2.102, 1.625, 1.063]
MOCKPRICES3 = [0.243, 0.282, 0.279, 0.303, 0.299, 0.314, 0.304, 0.377, 0.482, 0.484, 0.482, 0.268, 0.171, 0.174, 0.171, 0.277, 0.52, 0.487, 0.51, 0.487, 0.451, 0.397, 0.331, 0.35]
MOCKPRICES4 = [0.629,0.37,0.304,0.452,0.652,1.484,2.704,3.693,3.64,3.275,2.838,2.684,2.606,1.463,0.916,0.782,0.793,1.199,1.825,2.108,1.909,1.954,1.168,0.268]
MOCKPRICES5 = [0.299,0.388,0.425,0.652,0.94,1.551,2.835,3.62,3.764,3.313,2.891,2.723,2.621,1.714,1.422,1.187,1.422,1.422,1.673,1.63,1.551,1.669,0.785,0.264]
MOCKPRICES6 = [1.057,1.028,0.826,0.87,1.15,1.754,2.42,2.918,3.262,3.009,2.594,2.408,2.364,2.34,2.306,2.376,2.494,2.626,2.626,2.516,2.564,2.565,2.489,1.314]
MOCKPRICES7 = [0.475, 1.051, 0.329, 0.396, 0.394, 2.049, 2.145, 3.019, 2.92, 2.534, 2.194, 2.12, 2.073, 1.86, 1.765, 1.578, 1.59, 1.943, 2.07, 2.098, 2.088, 2.041, 1.888, 0.475]
MOCKPRICES_FLAT = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
MOCKPRICES_SHORT = [0.51, 0.487, 0.451, 0.397, 0.331, 0.35]
PRICES_BLANK = ",,,,,,,,,,,,,,,,,,,,,,,"
PRICS_ARRAY_WITH_STRING = "6,6,6,6,6,6,6,6,hej,6,6,6,6,6,6"
PRICES_ARRAYSTR = "6.0,6.0,6.0,6.06,6.0,6.0,6.6,6,6,6,6,6,6,6"
MOCKPRICES6 = [1.057, 1.028, 0.826, 0.87, 1.15, 1.754, 2.42, 2.918, 3.262, 3.009, 2.594, 2.408, 2.364, 2.34, 2.306, 2.376, 2.494, 2.626, 2.626, 2.516, 2.564, 2.565, 2.489, 1.314]
MOCKPRICES_CHEAP = [0.042, 0.034, 0.026, 0.022, 0.02, 0.023, 0.027, 0.037, 0.049, 0.068, 0.08, 0.093, 0.093, 0.091, 0.103, 0.178, 0.36, 0.427, 1.032, 0.972, 0.551, 0.628, 0.404, 0.355]
MOCKPRICES_EXPENSIVE = [0.366, 0.359, 0.357, 0.363, 0.402, 2.026, 4.036, 4.935, 6.689, 4.66, 4.145, 4.094, 3.526, 2.861, 2.583, 2.456, 2.414, 2.652, 2.799, 3.896, 4.232, 4.228, 3.824, 2.084]
MOCK220621 = [1.987, 1.813, 0.996, 0.527, 0.759, 1.923, 3.496, 4.512, 4.375, 3.499, 2.602, 2.926, 2.857, 2.762, 2.354, 2.678, 3.117, 2.384, 3.062, 2.376, 2.245, 2.046, 1.84, 0.372]
MOCK220622 = [0.142, 0.106, 0.1, 0.133, 0.266, 0.412, 2.113, 3, 4.98, 4.374, 3.913, 3.796, 3.491, 3.241, 3.173, 2.647, 2.288, 2.254, 2.497, 2.247, 2.141, 2.2, 2.113, 0.363]

def test_mockprices1_non_hours():
    r = h(base_mock_hour=21)
    r.prices = MOCKPRICES1
    r.update()
    assert r.non_hours == [21]

def test_mockprices1_caution_hours():
    r = h(base_mock_hour=21)
    r.prices = MOCKPRICES1
    r.update()
    assert r.caution_hours == [22]

def test_mockprices1_caution_hours_aggressive():
    # this test breaks sometimes and i do not know why.
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_AGGRESSIVE])
    r.prices = MOCKPRICES1
    r.update(21)
    assert r.caution_hours == [22]

def test_mockprices1_caution_hours_per_type():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_AGGRESSIVE])
    r.prices = MOCKPRICES1
    r.update(21)
    r2 = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE])
    r2.prices = MOCKPRICES1
    r2.update(21)
    r3 = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE])
    r3.prices = MOCKPRICES1
    r3.update(21)
    assert len(r.caution_hours) <= len(r2.caution_hours)
    assert len(r2.caution_hours) <= len(r3.caution_hours)
    assert len(r.non_hours) >= len(r2.non_hours)
    assert len(r2.non_hours) >= len(r3.non_hours)
    
def test_mockprices2_non_hours():
    r = h(base_mock_hour=21)
    r.prices = MOCKPRICES2
    r.update()
    assert r.non_hours == [21]

def test_mockprices2_caution_hours():
    r = h(base_mock_hour=21)
    r.prices = MOCKPRICES2
    r.update()
    assert r.caution_hours == [22,23]

def test_mockprices3_non_hours():
    r = h(base_mock_hour=21)
    r.prices = MOCKPRICES3
    r.update()
    assert r.non_hours == [21]

def test_mockprices3_caution_hours():
    r = h(base_mock_hour=21)
    r.prices = MOCKPRICES3
    r.update()
    assert r.caution_hours == [22,23]

def test_cautionhour_over_max_error():
    with pytest.raises(AssertionError):
        h(cautionhour_type=2)
    
def test_cautionhour_zero_error():
    with pytest.raises(AssertionError):
        h(cautionhour_type=0)

def test_cautionhour_negative_error():
    with pytest.raises(AssertionError):
        h(cautionhour_type=-1)

def test_create_dict():
    r = h()
    ret = HourSelectionHelpers._create_dict(MOCKPRICES1)
    assert ret[20] == 2.603
    assert len(ret) == 24

def test_create_dict_error():
    r = h()
    with pytest.raises(ValueError):
              HourSelectionHelpers._create_dict(MOCKPRICES_SHORT)

# def test_rank_prices():
#     r = h()
#     hourly = r._create_dict(MOCKPRICES1)
#     norm_hourly = r._create_dict(r._normalize_prices(MOCKPRICES1))
#     ret = r._rank_prices(hourly, norm_hourly)
#     assert ret == {6: {'permax': 0.37, 'val': 1}, 7: {'permax': 0.96, 'val': 2.572}, 8: {'permax': 1.0, 'val': 2.688}, 9: {'permax': 1.0, 'val': 2.677}, 10: {'permax': 0.99, 'val': 2.648}, 11: {'permax': 0.96, 'val': 2.571}, 12: {'permax': 0.95, 'val': 2.561}, 13: {'permax': 0.77, 'val': 2.07}, 14: {'permax': 0.77, 'val': 2.083}, 15: {'permax': 0.91, 'val': 2.459}, 16: {'permax': 0.93, 'val': 2.508}, 17: {'permax': 0.96, 'val': 2.589}, 18: {'permax': 0.98, 'val': 2.647}, 19: {'permax': 0.99, 'val': 2.648}, 20: {'permax': 0.97, 'val': 2.603}, 21: {'permax': 0.96, 'val': 2.588}, 22: {'permax': 0.53, 'val': 1.424}} == {6: {'permax': 0.37, 'val': 1}, 7: {'permax': 0.96, 'val': 2.572}, 8: {'permax': 1.0, 'val': 2.688}, 9: {'permax': 1.0, 'val': 2.677}, 10: {'permax': 0.99, 'val': 2.648}, 11: {'permax': 0.96, 'val': 2.571}, 12: {'permax': 0.95, 'val': 2.561}, 13: {'permax': 0.77, 'val': 2.07}, 14: {'permax': 0.77, 'val': 2.083}, 15: {'permax': 0.91, 'val': 2.459}, 16: {'permax': 0.93, 'val': 2.508}, 17: {'permax': 0.96, 'val': 2.589}, 18: {'permax': 0.98, 'val': 2.647}, 19: {'permax': 0.99, 'val': 2.648}, 20: {'permax': 0.97, 'val': 2.603}, 21: {'permax': 0.96, 'val': 2.588}, 22: {'permax': 0.53, 'val': 1.424}, 23: {'permax': 0.22, 'val': 0.595}}

def test_rank_prices_permax():
    r = h()
    hourly = HourSelectionHelpers._create_dict(MOCKPRICES1)
    norm_hourly = HourSelectionHelpers._create_dict(HourSelectionCalculations.normalize_prices(MOCKPRICES1))
    ret = HourSelectionCalculations.rank_prices(hourly, norm_hourly)
    for r in ret:
        assert 0 <= ret[r]["permax"] <= 1

# def test_rank_prices_flat_curve():
#     r = h()
#     hourly = r._create_dict(MOCKPRICES_FLAT)
#     norm_hourly = r._create_dict(r._normalize_prices(MOCKPRICES_FLAT))
#     ret = r._rank_prices(hourly, norm_hourly)
#     assert ret == {}

def test_add_expensive_non_hours():
    r = h()
    pass

def test_add_expensive_non_hours_flat_curve():
    r = h(absolute_top_price=0.5, base_mock_hour=18)
    r.prices = MOCKPRICES_FLAT
    r.update()
    assert len(r.non_hours) == 6

def test_add_expensive_non_hours_error():
    r = h()
    pass

def test_determine_hours():
    r = h()
    pass

def test_determine_hours_error():
    r = h()
    pass


def test_mockprices4_suave():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], base_mock_hour=0)
    r.prices = MOCKPRICES4
    r.update()
    assert r.non_hours ==[7,8,9,10]
    assert r.caution_hours ==[5,6,11,12,13,17,18,19,20,21,22]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours

def test_mockprices4_intermediate():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], base_mock_hour=0)
    r.prices = MOCKPRICES4
    r.update()
    assert r.non_hours==[6,7,8,9,10,11,12,19,20,21]
    assert r.caution_hours ==[5,13,17,18,22] 
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours

def test_mockprices4_aggressive():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_AGGRESSIVE], base_mock_hour=0)
    r.prices = MOCKPRICES4
    r.update()
    assert r.non_hours == [6,7,8,9,10,11,12,18,19,20,21]
    assert r.caution_hours == [5,13,17,22]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours

def test_mockprices5_suave():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], base_mock_hour=0)
    r.prices = MOCKPRICES5
    r.update()
    assert r.non_hours == [7,8,9,10]
    assert r.caution_hours == [5,6,11,12,13,14,15,16,17,18,19,20,21]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours

def test_mockprices5_intermediate():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], base_mock_hour=0)
    r.prices = MOCKPRICES5
    r.update()
    assert r.non_hours == [6,7,8,9,10,11,12]
    assert r.caution_hours == [5,13,14,15,16,17,18,19,20,21]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours

def test_mockprices5_aggressive():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_AGGRESSIVE], base_mock_hour=0)
    r.prices = MOCKPRICES5
    r.update()
    assert r.non_hours == [6,7,8,9,10,11,12,13]
    assert r.caution_hours == [5,14,15,16,17,18,19,20,21]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours


def test_dynamic_cautionhours_no_max_price_suave():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], base_mock_hour=0)
    r.prices = MOCKPRICES5
    r.update()
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert r.non_hours == [7, 8, 9, 10]
    assert r.dynamic_caution_hours == {5: 0.74, 6: 0.4, 11: 0.43, 12: 0.45, 13: 0.69, 14: 0.77, 15: 0.83, 16: 0.77, 17: 0.77, 18: 0.71, 19: 0.72, 20: 0.74, 21: 0.71}

def test_dynamic_cautionhours_with_max_price_suave():
    r = h(absolute_top_price=2, cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], base_mock_hour=0)
    r.prices = MOCKPRICES5
    r.update()
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert r.non_hours == [6, 7, 8, 9, 10,11,12]
    assert r.dynamic_caution_hours == {5: 0.74, 13: 0.69, 14: 0.77, 15: 0.83, 16: 0.77, 17: 0.77, 18: 0.71, 19: 0.72, 20: 0.74, 21: 0.71}


def test_dynamic_cautionhours_no_max_price_aggressive():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_AGGRESSIVE], base_mock_hour=0)
    r.prices = MOCKPRICES5
    r.update()
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert r.non_hours == [6, 7, 8, 9, 10, 11, 12,13]

def test_prices7():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_AGGRESSIVE], base_mock_hour=0)
    r.prices = MOCKPRICES7
    r.update()
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert r.non_hours == [5, 6, 7, 8, 9, 10, 11, 12,13,14,17,18,19,20,21,22]


def test_dynamic_cautionhours_very_low_peaqstdev():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], base_mock_hour=0)
    r.prices = MOCKPRICES6
    r.update()
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert len(r.non_hours) + len(r.dynamic_caution_hours) < 24
    

def test_total_charge_just_today():
    MOCKHOUR = 0
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE],base_mock_hour=MOCKHOUR)
    r.prices = MOCKPRICES1
    r.update()
    assert r.get_total_charge(2, MOCKHOUR) == 17.2

def test_total_charge_today_tomorrow():
    MOCKHOUR = 18
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], base_mock_hour=MOCKHOUR)
    r.prices = MOCKPRICES1
    r.prices_tomorrow = MOCKPRICES2
    r.update()
    assert r.get_total_charge(2, MOCKHOUR) == 36.5

def test_average_kwh_price_just_today():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE])
    MOCKHOUR = 0
    r.prices = MOCKPRICES1
    r.update(MOCKHOUR)
    assert r.get_average_kwh_price(MOCKHOUR) == 0.35

def test_average_kwh_price_today_tomorrow():
    MOCKHOUR = 18
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE])
    r.prices = MOCKPRICES1
    r.prices_tomorrow = MOCKPRICES2
    r.update(MOCKHOUR)
    assert r.get_average_kwh_price(MOCKHOUR) == 0.61

def test_cheap_today_expensive_tomorrow_top_up():
    MOCKHOUR = 14
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], allow_top_up=True, base_mock_hour=MOCKHOUR)
    r.prices = MOCKPRICES_CHEAP
    r.prices_tomorrow = MOCKPRICES_EXPENSIVE
    r.update()
    assert r.non_hours == [5, 6, 7, 8, 9, 10, 11, 12,13]
    assert r.dynamic_caution_hours == {}

def test_cheap_today_expensive_tomorrow_top_up_top_price():
    MOCKHOUR = 22
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], allow_top_up=True, base_mock_hour=MOCKHOUR, absolute_top_price=1)
    r.prices = MOCK220621
    r.prices_tomorrow = MOCK220622
    r.update()
    assert r.non_hours == [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]

def test_cheap_today_expensive_tomorrow_no_top_up():
    MOCKHOUR = 14
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], allow_top_up=False, base_mock_hour=MOCKHOUR)
    r.prices = MOCKPRICES_CHEAP
    r.prices_tomorrow = MOCKPRICES_EXPENSIVE
    assert r.non_hours == [5,6,7,8,9,10,11,12,13]
    assert r.dynamic_caution_hours == {}

def test_expensive_today_cheap_tomorrow_top_up():
    MOCKHOUR = 14
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], allow_top_up=True, base_mock_hour=MOCKHOUR)
    r.prices = MOCKPRICES_EXPENSIVE
    r.prices_tomorrow = MOCKPRICES_CHEAP
    assert r.non_hours == [14, 15, 16, 17, 18, 19,20,21,22,23]
    assert r.dynamic_caution_hours == {}
    
def test_expensive_today_cheap_tomorrow_no_top_up():
    MOCKHOUR = 14
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], allow_top_up=False, base_mock_hour=MOCKHOUR)
    r.prices = MOCKPRICES_EXPENSIVE
    r.prices_tomorrow = MOCKPRICES_CHEAP
    assert r.non_hours == [14, 15, 16, 17, 18, 19,20,21,22,23]

def test_new_test():
    MOCKHOUR = 13
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=2.0, min_price=0.5, allow_top_up=False, base_mock_hour=MOCKHOUR)
    r.prices = [0.142, 0.106, 0.1, 0.133, 0.266, 0.412, 2.113, 3, 4.98, 4.374, 3.913, 3.796, 3.491, 3.241, 3.173, 2.647, 2.288, 2.254, 2.497, 2.247, 2.141, 2.2, 2.113, 0.363]
    r.prices_tomorrow = [0.063, 0.039, 0.032, 0.034, 0.043, 0.274, 0.539, 1.779, 2.002, 1.75, 1.388, 1.195, 1.162, 0.962, 0.383, 0.387, 0.63, 1.202, 1.554, 1.75, 1.496, 1.146, 0.424, 0.346]
    assert r.non_hours == [13,14,15,16,17,18,19,20,21,22,7,8,9,10]

def test_new_test_2():
    MOCKHOUR = 13
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=2.0, min_price=0.5, allow_top_up=True, base_mock_hour=MOCKHOUR)
    r.prices = [0.142, 0.106, 0.1, 0.133, 0.266, 0.412, 2.113, 3, 4.98, 4.374, 3.913, 3.796, 3.491, 3.241, 3.173, 2.647, 2.288, 2.254, 2.497, 2.247, 2.141, 2.2, 2.113, 0.363]
    r.prices_tomorrow = [0.063, 0.039, 0.032, 0.034, 0.043, 0.274, 0.539, 1.779, 2.002, 1.75, 1.388, 1.195, 1.162, 0.962, 0.383, 0.387, 0.63, 1.202, 1.554, 1.75, 1.496, 1.146, 0.424, 0.346]
    assert r.non_hours == [8,13,14,15,16,17,18,19,20,21,22]
    
def test_new_test_3():
    MOCKHOUR = 13
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], absolute_top_price=0, min_price=0.5, allow_top_up=True, base_mock_hour=MOCKHOUR)
    r.prices = [0.142, 0.106, 0.1, 0.133, 0.266, 0.412, 2.113, 3, 4.98, 4.374, 3.913, 3.796, 3.491, 3.241, 3.173, 2.647, 2.288, 2.254, 2.497, 2.247, 2.141, 2.2, 2.113, 0.363]
    r.prices_tomorrow = [0.063, 0.039, 0.032, 0.034, 0.043, 0.274, 0.539, 1.779, 2.002, 1.75, 1.388, 1.195, 1.162, 0.962, 0.383, 0.387, 0.63, 1.202, 1.554, 1.75, 1.496, 1.146, 0.424, 0.346]
    assert r.non_hours == [13, 14, 15, 16, 17, 18, 19, 20,21,22]
    assert r.dynamic_caution_hours == {}

def test_new_test_4():
    MOCKHOUR = 13
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=0, min_price=0.5, allow_top_up=True, base_mock_hour=MOCKHOUR)
    r.prices = [0.142, 0.106, 0.1, 0.133, 0.266, 0.412, 2.113, 3, 4.98, 4.374, 3.913, 3.796, 3.491, 3.241, 3.173, 2.647, 2.288, 2.254, 2.497, 2.247, 2.141, 2.2, 2.113, 0.363]
    r.prices_tomorrow = [0.063, 0.039, 0.032, 0.034, 0.043, 0.274, 0.539, 1.779, 2.002, 1.75, 1.388, 1.195, 1.162, 0.962, 0.383, 0.387, 0.63, 1.202, 1.554, 1.75, 1.496, 1.146, 0.424, 0.346]
    assert r.non_hours == [13,14,15,16,17,18,19,20,21,22]
    
def test_negative_prices():
    MOCKHOUR = 13
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=0, min_price=0.5, allow_top_up=False, base_mock_hour=MOCKHOUR)
    r.prices = [0.021,0.02,0.02,0.019,0.019,0.019,0.018,0.019,0.019,0.02,0.02,0.014,0.001,-0.001,-0.001,0,0.014,0.019,0.02,0.744,2.23,0.463,0.024,0.019]
    r.prices_tomorrow = [0.02,0.019,0.019, 0.019, 0.019, 0.02, 0.02,0.02,0.024, 0.037, 0.047, 0.052, 0.052, 0.054, 0.058, 0.064, 0.1, 0.17, 0.212, 0.529, 0.792, 0.331, 0.394, 0.18]
    assert r.non_hours == [19,20,21]


def test_allow_top_up_extreme_2():
    MOCKHOUR = 13
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=0, min_price=0.5, allow_top_up=False, base_mock_hour=MOCKHOUR)
    r.prices = [1.032, 0.663, 0.663, 0.699, 0.842, 1.102, 4.764, 4.949, 5.9, 7.612, 7.493, 7.245, 6.987, 6.464, 5.958, 5.959, 6.342, 6.685, 7.049, 5.957, 5.332, 4.74, 3.045, 0.663]
    r.prices_tomorrow = [0.798, 0.797, 0.727, 0.755, 0.513, 0.456, 0.349, 0.447, 0.928, 2.323, 2.349, 1.062, 0.37, 0.221, 0.211, 0.28, 0.362, 0.716, 1.038, 1.05, 0.826, 0.496, 0.307, 0.133]
    r.service._base_mock_hour = 20
    assert r.non_hours == [20,21,22]

def test_allow_top_up_extreme_1():
    MOCKHOUR = 13
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=0, min_price=0.5, allow_top_up=True, base_mock_hour=MOCKHOUR)
    r.prices = [1.032, 0.663, 0.663, 0.699, 0.842, 1.102, 4.764, 4.949, 5.9, 7.612, 7.493, 7.245, 6.987, 6.464, 5.958, 5.959, 6.342, 6.685, 7.049, 5.957, 5.332, 4.74, 3.045, 0.663]
    r.prices_tomorrow = [0.798, 0.797, 0.727, 0.755, 0.513, 0.456, 0.349, 0.447, 0.928, 2.323, 2.349, 1.062, 0.37, 0.221, 0.211, 0.28, 0.362, 0.716, 1.038, 1.05, 0.826, 0.496, 0.307, 0.133]
    r.service._base_mock_hour = 20
    r.update()
    assert r.non_hours == [20,21,22]

def test_over_midnight_top_up_conserve_top_up():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=0, min_price=0, allow_top_up=True)
    
    r.service._base_mock_hour = 13
    r.prices = [0.019, 0.015, 0.014, 0.013, 0.013, 0.017, 0.019, 0.067, 0.157, 0.199, 0.177, 0.131, 0.025, 0.022, 0.02, 0.021, 0.024, 0.323, 1.94, 1.97, 1.5, 0.677, 1.387, 0.227]
    r.prices_tomorrow = [0.046, 0.026, 0.035, 0.066, 0.135, 0.359, 2.154, 3.932, 5.206, 4.947, 3.848, 2.991, 2.457, 2.492, 2.273, 2.177, 2.142, 2.555, 2.77, 2.185, 2.143, 1.318, 0.021, 0.02]
    assert r.non_hours == [6, 7, 8, 9, 10, 11,12]
    #assert r.model.options.conserve_top_up is True
    
    r.service._base_mock_hour = 23
    assert r.non_hours == [6, 7, 8, 9, 10, 11,12,13]
    #assert r.model.options.conserve_top_up is True
    
    r.service._base_mock_hour = 2
    r.prices = [0.046, 0.026, 0.035, 0.066, 0.135, 0.359, 2.154, 3.932, 5.206, 4.947, 3.848, 2.991, 2.457, 2.492, 2.273, 2.177, 2.142, 2.555, 2.77, 2.185, 2.143, 1.318, 0.021, 0.02]
    r.prices_tomorrow = []
    #assert r.model.options.conserve_top_up is True
    
    r.service._base_mock_hour = 13
    assert r.non_hours == []
    r.prices_tomorrow = [0.798, 0.797, 0.727, 0.755, 0.513, 0.456, 0.349, 0.447, 0.928, 2.323, 2.349, 1.062, 0.37, 0.221, 0.211, 0.28, 0.362, 0.716, 1.038, 1.05, 0.826, 0.496, 0.307, 0.133]
    assert r.model.options.conserve_top_up is False
    
    assert r.non_hours == [13,14,15,16,17,18,19,20,9,10]

def test_over_midnight_no_top_up():
    MOCKHOUR = 23
    MOCKHOUR2 = 2
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=0, min_price=0, allow_top_up=False)
    r.prices = [0.019, 0.015, 0.014, 0.013, 0.013, 0.017, 0.019, 0.067, 0.157, 0.199, 0.177, 0.131, 0.025, 0.022, 0.02, 0.021, 0.024, 0.323, 1.94, 1.97, 1.5, 0.677, 1.387, 0.227]
    r.prices_tomorrow = [0.046, 0.026, 0.035, 0.066, 0.135, 0.359, 2.154, 3.932, 5.206, 4.947, 3.848, 2.991, 2.457, 2.492, 2.273, 2.177, 2.142, 2.555, 2.77, 2.185, 2.143, 1.318, 0.021, 0.02]
    r.update(testhour=MOCKHOUR)
    assert r.non_hours == [6,7, 8, 9,10,11,12,13]
    r.prices = [0.046, 0.026, 0.035, 0.066, 0.135, 0.359, 2.154, 3.932, 5.206, 4.947, 3.848, 2.991, 2.457, 2.492, 2.273, 2.177, 2.142, 2.555, 2.77, 2.185, 2.143, 1.318, 0.021, 0.02]
    r.prices_tomorrow = []
    r.update(MOCKHOUR2)
    assert r.non_hours == [7,8,9]


def test_very_high_prices():
    MOCKHOUR = 19
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=0, min_price=0, allow_top_up=False)
    r.prices = [2.801, 2.265, 2.08, 2.265, 3.065, 4.704, 5.84, 8.691, 9.062, 8.53, 8.182, 7.348, 6.912, 6.909, 7.327, 7.597, 7.995, 8.43, 9.282, 9.987, 8.33, 7.795, 5.93, 4.052]
    r.prices_tomorrow = [3.452, 1.311, 0.664, 0.664, 0.664, 3.37, 4.715, 6.25, 6.791, 7.457, 7.612, 7.467, 6.681, 6.367, 6.92, 6.871, 6.63, 6.804, 7.095, 6.63, 5.723, 7.321, 5.717, 3.386]
    r.update(testhour=13)
    r.service._base_mock_hour = MOCKHOUR   
    assert r.non_hours == [19, 20, 21, 22,7, 8, 9,10,11,12,13,14,15,16,17,18]

def test_top_up5():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], absolute_top_price=0, min_price=0, allow_top_up=True)
    r.prices = [0.619, 0.613, 0.622, 0.634, 0.639, 0.687, 0.767, 0.937, 1.035, 1.049, 1.039, 1.036, 1.033, 1.038, 1.043, 1.044, 0.981, 1.031, 1.028, 1.027, 1.042, 0.954, 0.95, 0.817]
    r.prices_tomorrow = [0.69, 0.706, 0.721, 0.688, 0.77, 0.863, 1.008, 1.263, 2.473, 2.065, 1.948, 2.499, 2.339, 3.133, 2.538, 2.861, 3.309, 4.258, 4.98, 4.904, 4.01, 3.351, 1.215, 1.065]
    r.service._base_mock_hour = 13
    assert r.non_hours == [8,9,10,11,12]
    r.service._base_mock_hour = 20
    #assert r.model.options.conserve_top_up is True
    assert r.non_hours == [8,9,10,11,13,14,15,16,17,18,19,20]
    r.service._base_mock_hour = 6
    assert r.model.options.conserve_top_up is True
    assert r.non_hours == [7,8,9,10,11]
    r.service._base_mock_hour = 7
    assert r.model.options.conserve_top_up is True
    assert r.non_hours == [7,8,9,10,11]
    r.service._base_mock_hour = 9
    assert r.model.options.conserve_top_up is True
    assert r.non_hours == [9,10,11]
    r.service._base_mock_hour = 10
    assert r.model.options.conserve_top_up is True
    assert r.non_hours == [10,11]

def test_top_up6():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], absolute_top_price=0, min_price=0, allow_top_up=True)
    r.prices = [0.858, 0.847, 0.682, 0.303, 0.238, 0.225, 0.22, 0.333, 0.614, 0.879, 0.876, 0.851, 0.75, 0.798, 0.828, 0.877, 0.93, 1.017, 1.102, 1.062, 0.924, 0.88, 0.911, 0.902]
    r.prices_tomorrow = [0.876, 0.869, 0.79, 0.84, 0.803, 0.808, 0.806, 0.814, 1.154, 1.248, 1.006, 0.863, 0.799, 0.784, 0.876, 0.909, 1.239, 2.543, 2.71, 2.3, 2.011, 3.052, 2.154, 1.998]
    r.service._base_mock_hour = 13
    assert r.non_hours == [16,17,18,19,20,8,9,10]

def test_regular5():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], absolute_top_price=0, min_price=0, allow_top_up=False)
    r.prices = [0.619, 0.613, 0.622, 0.634, 0.639, 0.687, 0.767, 0.937, 1.035, 1.049, 1.039, 1.036, 1.033, 1.038, 1.043, 1.044, 0.981, 1.031, 1.028, 1.027, 1.042, 0.954, 0.95, 0.817]
    r.service._base_mock_hour = 0
    assert r.non_hours == [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]
    r.prices_tomorrow = [0.69, 0.706, 0.721, 0.688, 0.77, 0.863, 1.008, 1.263, 2.473, 2.065, 1.948, 2.499, 2.339, 3.133, 2.538, 2.861, 3.309, 4.258, 4.98, 4.904, 4.01, 3.351, 1.215, 1.065]
    r.service._base_mock_hour = 13
    assert r.non_hours == [8,9,10,11,12]
    r.service._base_mock_hour = 22
    assert r.non_hours == [8, 9, 10, 11, 12, 13,14,15,16,17,18,19,20,21]

def test_regular5_max_price():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], absolute_top_price=0.7, min_price=0, allow_top_up=False)
    r.prices = [0.619, 0.613, 0.622, 0.634, 0.639, 0.687, 0.767, 0.937, 1.035, 1.049, 1.039, 1.036, 1.033, 1.038, 1.043, 1.044, 0.981, 1.031, 1.028, 1.027, 1.042, 0.954, 0.95, 0.817]
    r.service._base_mock_hour = 0
    assert r.non_hours == [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    r.prices_tomorrow = [0.69, 0.706, 0.721, 0.688, 0.77, 0.863, 1.008, 1.263, 2.473, 2.065, 1.948, 2.499, 2.339, 3.133, 2.538, 2.861, 3.309, 4.258, 4.98, 4.904, 4.01, 3.351, 1.215, 1.065]
    r.service._base_mock_hour = 13
    assert r.non_hours == [13,14,15,16,17,18,19,20,21,22,23,1,2,4,5,6,7,8,9,10,11,12]
    
def test_regular6():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], absolute_top_price=0, min_price=0, allow_top_up=False)
    r.prices = [0.619, 0.613, 0.622, 0.634, 0.639, 0.687, 0.767, 0.937, 1.035, 1.049, 1.039, 1.036, 1.033, 1.038, 1.043, 1.044, 0.981, 1.031, 1.028, 1.027, 1.042, 0.954, 0.95, 0.817]
    r.service._base_mock_hour = 0
    assert r.non_hours == [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]

def test_regular7():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_INTERMEDIATE], absolute_top_price=0, min_price=0, allow_top_up=False)
    r.prices = [0.69, 0.706, 0.721, 0.688, 0.77, 0.863, 1.008, 1.263, 2.473, 2.065, 1.948, 2.499, 2.339, 3.133, 2.538, 2.861, 3.309, 4.258, 4.98, 4.904, 4.01, 3.351, 1.215, 1.065]
    r.service._base_mock_hour = 0
    assert r.non_hours == [13, 14, 15, 16, 17, 18,19,20,21]
    


def test_remove_tomorrow():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=0, min_price=0, allow_top_up=False)
    r.service._base_mock_hour = 13
    r.prices = [2.801, 2.265, 2.08, 2.265, 3.065, 4.704, 5.84, 8.691, 9.062, 8.53, 8.182, 7.348, 6.912, 6.909, 7.327, 7.597, 7.995, 8.43, 9.282, 9.987, 8.33, 7.795, 5.93, 4.052]
    r.prices_tomorrow = [3.452, 1.311, 0.664, 0.664, 0.664, 3.37, 4.715, 6.25, 6.791, 7.457, 7.612, 7.467, 6.681, 6.367, 6.92, 6.871, 6.63, 6.804, 7.095, 6.63, 5.723, 7.321, 5.717, 3.386]
    r.service._base_mock_hour = 0
    r.prices = [3.452, 1.311, 0.664, 0.664, 0.664, 3.37, 4.715, 6.25, 6.791, 7.457, 7.612, 7.467, 6.681, 6.367, 6.92, 6.871, 6.63, 6.804, 7.095, 6.63, 5.723, 7.321, 5.717, 3.386]
    assert r.prices_tomorrow == []

def test_set_tomorrow_as_comma_string():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_SUAVE], absolute_top_price=0, min_price=0, allow_top_up=False)
    r.service._base_mock_hour = 13
    r.prices = [2.801, 2.265, 2.08, 2.265, 3.065, 4.704, 5.84, 8.691, 9.062, 8.53, 8.182, 7.348, 6.912, 6.909, 7.327, 7.597, 7.995, 8.43, 9.282, 9.987, 8.33, 7.795, 5.93, 4.052]
    r.prices_tomorrow = [3.452, 1.311, 0.664, 0.664, 0.664, 3.37, 4.715, 6.25, 6.791, 7.457, 7.612, 7.467, 6.681, 6.367, 6.92, 6.871, 6.63, 6.804, 7.095, 6.63, 5.723, 7.321, 5.717, 3.386]
    r.service._base_mock_hour = 0
    r.prices = [3.452, 1.311, 0.664, 0.664, 0.664, 3.37, 4.715, 6.25, 6.791, 7.457, 7.612, 7.467, 6.681, 6.367, 6.92, 6.871, 6.63, 6.804, 7.095, 6.63, 5.723, 7.321, 5.717, 3.386]
    r.prices_tomorrow = PRICES_BLANK
    assert r.prices_tomorrow == []

def test_top_up2():
    r = h(cautionhour_type=CAUTIONHOURTYPE[CAUTIONHOURTYPE_AGGRESSIVE], absolute_top_price=0, min_price=0, allow_top_up=True)
    r.service._base_mock_hour = 0
    r.prices = [1.4005, 1.1325, 1.04, 1.1325, 1.5325, 2.352, 2.92, 4.3455, 4.531, 4.265, 4.091, 3.674, 3.456, 3.4545, 3.6635, 3.7985, 3.9975, 4.215, 4.641, 4.9935, 4.165, 3.8975, 2.965, 2.026]
    assert r.non_hours == [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
    r.service._base_mock_hour = 13
    r.prices_tomorrow = [0.042, 0.034, 0.026, 0.022, 0.02, 0.023, 0.027, 0.037, 0.049, 0.068, 0.08, 0.093, 0.093, 0.091, 0.103, 0.178, 0.36, 0.427, 1.032, 0.972, 0.551, 0.628, 0.404, 0.355]
    r.service._base_mock_hour = 23
    assert r.non_hours == [23,17,18,19,20,21]




