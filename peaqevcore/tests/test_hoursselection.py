from datetime import date, datetime
import pytest
import statistics as stat
from ..services.hourselection.hoursselection import Hoursselection as h
from ..services.hourselection.hourselectionservice.hourselection_calculations import (
    async_create_cautions,
    normalize_prices,
)
from ..services.hourselection.hourselectionservice.hoursselection_helpers import (
    async_create_dict,
)
from ..models.hourselection.cautionhourtype import CautionHourType, VALUES_CONVERSION
from ..models.hourselection.topprice_type import TopPriceType
from .prices import *


@pytest.mark.asyncio
async def test_mockprices1_non_hours():
    r = h()
    r.service.dtmodel.set_hour(21)
    prices = MOCKPRICES1
    await r.async_update_prices(prices)
    assert r.non_hours == [21]


@pytest.mark.asyncio
async def test_mockprices1_caution_hours():
    r = h()
    r.service.dtmodel.set_hour(21)
    prices = MOCKPRICES1
    await r.async_update_prices(prices)
    assert r.caution_hours == [22]


@pytest.mark.asyncio
async def test_mockprices1_caution_hours_aggressive():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE)
    prices = MOCKPRICES1
    r.service.dtmodel.set_hour(21)
    await r.async_update_prices(prices)
    assert r.caution_hours == [22]


@pytest.mark.asyncio
async def test_mockprices1_caution_hours_per_type():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE)
    prices = MOCKPRICES1
    r.service.dtmodel.set_hour(21)
    await r.async_update_prices(prices)
    r2 = h(cautionhour_type=CautionHourType.INTERMEDIATE)
    prices2 = MOCKPRICES1
    r2.service.dtmodel.set_hour(21)
    await r2.async_update_prices(prices2)
    r3 = h(cautionhour_type=CautionHourType.SUAVE)
    prices3 = MOCKPRICES1
    r3.service.dtmodel.set_hour(21)
    await r3.async_update_prices(prices3)
    assert len(r.caution_hours) <= len(r2.caution_hours)
    assert len(r2.caution_hours) <= len(r3.caution_hours)
    assert len(r.non_hours) >= len(r2.non_hours)
    assert len(r2.non_hours) >= len(r3.non_hours)


@pytest.mark.asyncio
async def test_mockprices2_non_hours():
    r = h()
    r.service.dtmodel.set_hour(21)
    prices = MOCKPRICES2
    await r.async_update_prices(prices)
    assert r.non_hours == [21]


@pytest.mark.asyncio
async def test_mockprices2_non_hours_unknown_tomorrow():
    r = h()
    r.service.dtmodel.set_hour(21)
    prices = MOCKPRICES2
    prices_tomorrow = ["unknown" for i in range(0, 24)]
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [21]


@pytest.mark.asyncio
async def test_mockprices2_caution_hours():
    r = h()
    prices = MOCKPRICES2
    r.service.dtmodel.set_hour(21)
    await r.async_update_prices(prices)
    assert r.caution_hours == [22, 23]


@pytest.mark.asyncio
async def test_mockprices3_non_hours():
    r = h()
    prices = MOCKPRICES3
    r.service.dtmodel.set_hour(21)
    await r.async_update_prices(prices)
    assert r.non_hours == [21]


@pytest.mark.asyncio
async def test_mockprices3_caution_hours():
    r = h()
    prices = MOCKPRICES3
    r.service.dtmodel.set_hour(21)
    await r.async_update_prices(prices)
    assert r.caution_hours == [22, 23]


@pytest.mark.asyncio
async def test_create_dict():
    ret = await async_create_dict(MOCKPRICES1)
    assert ret[20] == 2.603
    assert len(ret) == 24


@pytest.mark.asyncio
async def test_create_dict_error():
    with pytest.raises(ValueError):
        await async_create_dict(MOCKPRICES_SHORT)


@pytest.mark.asyncio
async def test_rank_prices_permax():
    hourly = await async_create_dict(MOCKPRICES1)
    norm_hourly = await async_create_dict(normalize_prices(MOCKPRICES1))
    ret = await async_create_cautions(hourly, norm_hourly, CautionHourType.SUAVE)
    for r in ret:
        assert 0 <= ret[r]["permax"] <= 1


@pytest.mark.asyncio
async def test_mockprices4_suave():
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES4
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert r.non_hours == [7, 8, 9, 10]
    assert r.caution_hours == [5, 6, 11, 12, 13, 18, 19, 20, 21]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours


@pytest.mark.asyncio
async def test_mockprices4_intermediate():
    r = h(cautionhour_type=CautionHourType.INTERMEDIATE)
    prices = MOCKPRICES4
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert r.non_hours == [6, 7, 8, 9, 10, 11, 12, 19, 20, 21]
    assert r.caution_hours == [5, 13, 18]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours


@pytest.mark.asyncio
async def test_mockprices4_aggressive():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE)
    prices = MOCKPRICES4
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert r.non_hours == [6, 7, 8, 9, 10, 11, 12, 18, 19, 20, 21]
    assert r.caution_hours == [5, 13]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours


@pytest.mark.asyncio
async def test_mockprices5_suave():
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES5
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert r.non_hours == [7, 8, 9, 10]
    assert r.caution_hours == [5, 6, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours


@pytest.mark.asyncio
async def test_mockprices5_intermediate():
    r = h(cautionhour_type=CautionHourType.INTERMEDIATE)
    prices = MOCKPRICES5
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert r.non_hours == [6, 7, 8, 9, 10, 11, 12]
    assert r.caution_hours == [5, 13, 14, 16, 17, 18, 19, 20, 21]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours


@pytest.mark.asyncio
async def test_mockprices5_aggressive():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE)
    prices = MOCKPRICES5
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert r.non_hours == [6, 7, 8, 9, 10, 11, 12, 13]
    assert r.caution_hours == [5, 14, 16, 17, 18, 19, 20, 21]
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours


@pytest.mark.asyncio
async def test_dynamic_cautionhours_no_max_price_suave():
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES5
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert r.non_hours == [7, 8, 9, 10]


@pytest.mark.asyncio
async def test_dynamic_cautionhours_with_max_price_suave():
    r = h(absolute_top_price=2, cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES5
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert r.non_hours == [6, 7, 8, 9, 10, 11, 12]


@pytest.mark.asyncio
async def test_dynamic_cautionhours_no_max_price_aggressive():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE)
    prices = MOCKPRICES5
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert r.non_hours == [6, 7, 8, 9, 10, 11, 12, 13]


@pytest.mark.asyncio
async def test_prices7():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE)
    prices = MOCKPRICES7
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert r.non_hours == [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22]


@pytest.mark.asyncio
async def test_dynamic_cautionhours_very_low_peaqstdev():
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES6
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert list(r.dynamic_caution_hours.keys()) == r.caution_hours
    assert len(r.non_hours) + len(r.dynamic_caution_hours) < 24


@pytest.mark.asyncio
async def test_total_charge_just_today():
    MOCKHOUR = 0
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES1
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices)
    ret = await r.async_get_total_charge(2)
    assert ret[0] == 17.1


@pytest.mark.asyncio
async def test_total_charge_today_tomorrow():
    MOCKHOUR = 18
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES1
    prices_tomorrow = MOCKPRICES2
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    ret = await r.async_get_total_charge(2)
    assert ret[0] == 33.9


@pytest.mark.asyncio
async def test_average_kwh_price_just_today():
    r = h(cautionhour_type=CautionHourType.SUAVE)
    MOCKHOUR = 0
    prices = MOCKPRICES1
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices)
    ret = await r.async_get_average_kwh_price()
    assert ret[0] == 0.34


@pytest.mark.asyncio
async def test_average_kwh_price_today_tomorrow():
    MOCKHOUR = 18
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES1
    prices_tomorrow = MOCKPRICES2
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    ret = await r.async_get_average_kwh_price()
    assert ret[0] == 0.53


@pytest.mark.asyncio
async def test_cheap_today_expensive_tomorrow_2():
    MOCKHOUR = 14
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES_CHEAP
    prices_tomorrow = MOCKPRICES_EXPENSIVE
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [8]
    assert r.dynamic_caution_hours == {
        5: 0.8,
        6: 0.46,
        7: 0.3,
        9: 0.34,
        10: 0.44,
        11: 0.45,
        12: 0.54,
        13: 0.66,
    }


@pytest.mark.asyncio
async def test_both_min_and_max_price():
    MOCKHOUR = 0
    r = h(
        cautionhour_type=CautionHourType.SUAVE,
        absolute_top_price=1,
        min_price=0.5,
    )
    r.service.dtmodel.set_hour(MOCKHOUR)
    prices = [
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        1.2,
        0.4,
        0.4,
        1.2,
        1.2,
        1.2,
    ]
    await r.async_update_prices(prices)
    assert r.non_hours == [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        21,
        22,
        23,
    ]


@pytest.mark.asyncio
async def test_cheap_today_expensive_tomorrow_top_price():
    MOCKHOUR = 20
    r = h(
        cautionhour_type=CautionHourType.SUAVE,
        absolute_top_price=1,
    )
    prices = MOCK220621
    prices_tomorrow = MOCK220622
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [
        20,
        21,
        22,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
    ]


@pytest.mark.asyncio
async def test_cheap_today_expensive_tomorrow():
    MOCKHOUR = 14
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES_CHEAP
    prices_tomorrow = MOCKPRICES_EXPENSIVE
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [8]
    assert r.dynamic_caution_hours == {
        5: 0.8,
        6: 0.46,
        7: 0.3,
        9: 0.34,
        10: 0.44,
        11: 0.45,
        12: 0.54,
        13: 0.66,
    }


@pytest.mark.asyncio
async def test_expensive_today_cheap_tomorrow_afternoon():
    MOCKHOUR = 14
    r = h(cautionhour_type=CautionHourType.INTERMEDIATE)
    prices = MOCKPRICES_EXPENSIVE
    prices_tomorrow = MOCKPRICES_CHEAP
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [14, 15, 16, 17, 18, 19, 20, 21, 22]
    assert r.dynamic_caution_hours == {23: 0.54}


@pytest.mark.asyncio
async def test_expensive_today_cheap_tomorrow_2():
    MOCKHOUR = 2
    r = h(cautionhour_type=CautionHourType.SUAVE)
    prices = MOCKPRICES_EXPENSIVE
    prices_tomorrow = MOCKPRICES_CHEAP
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [8]
    assert r.caution_hours == [
        6,
        7,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
    ]


@pytest.mark.asyncio
async def test_new_test():
    MOCKHOUR = 13
    r = h(
        cautionhour_type=CautionHourType.SUAVE,
        absolute_top_price=2.0,
        min_price=0.5,
    )
    prices = [
        0.142,
        0.106,
        0.1,
        0.133,
        0.266,
        0.412,
        2.113,
        3,
        4.98,
        4.374,
        3.913,
        3.796,
        3.491,
        3.241,
        3.173,
        2.647,
        2.288,
        2.254,
        2.497,
        2.247,
        2.141,
        2.2,
        2.113,
        0.363,
    ]
    prices_tomorrow = [
        0.063,
        0.039,
        0.032,
        0.034,
        0.043,
        0.274,
        0.539,
        1.779,
        2.002,
        1.75,
        1.388,
        1.195,
        1.162,
        0.962,
        0.383,
        0.387,
        0.63,
        1.202,
        1.554,
        1.75,
        1.496,
        1.146,
        0.424,
        0.346,
    ]
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 8]


@pytest.mark.asyncio
async def test_new_test_3():
    MOCKHOUR = 13
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE,
        absolute_top_price=0,
        min_price=0.5,
    )
    prices = [
        0.142,
        0.106,
        0.1,
        0.133,
        0.266,
        0.412,
        2.113,
        3,
        4.98,
        4.374,
        3.913,
        3.796,
        3.491,
        3.241,
        3.173,
        2.647,
        2.288,
        2.254,
        2.497,
        2.247,
        2.141,
        2.2,
        2.113,
        0.363,
    ]
    prices_tomorrow = [
        0.063,
        0.039,
        0.032,
        0.034,
        0.043,
        0.274,
        0.539,
        1.779,
        2.002,
        1.75,
        1.388,
        1.195,
        1.162,
        0.962,
        0.383,
        0.387,
        0.63,
        1.202,
        1.554,
        1.75,
        1.496,
        1.146,
        0.424,
        0.346,
    ]
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 7, 8, 9]
    assert r.dynamic_caution_hours == {10: 0.6, 11: 0.66, 12: 0.67}


@pytest.mark.asyncio
async def test_negative_prices():
    MOCKHOUR = 13
    r = h(
        cautionhour_type=CautionHourType.SUAVE,
        absolute_top_price=0,
        min_price=0.5,
    )
    prices = [
        0.021,
        0.02,
        0.02,
        0.019,
        0.019,
        0.019,
        0.018,
        0.019,
        0.019,
        0.02,
        0.02,
        0.014,
        0.001,
        -0.001,
        -0.001,
        0,
        0.014,
        0.019,
        0.02,
        0.744,
        2.23,
        0.463,
        0.024,
        0.019,
    ]
    prices_tomorrow = [
        0.02,
        0.019,
        0.019,
        0.019,
        0.019,
        0.02,
        0.02,
        0.02,
        0.024,
        0.037,
        0.047,
        0.052,
        0.052,
        0.054,
        0.058,
        0.064,
        0.1,
        0.17,
        0.212,
        0.529,
        0.792,
        0.331,
        0.394,
        0.18,
    ]
    r.service.dtmodel.set_hour(MOCKHOUR)
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [20]


@pytest.mark.asyncio
async def test_over_midnight():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    prices = [
        0.019,
        0.015,
        0.014,
        0.013,
        0.013,
        0.017,
        0.019,
        0.067,
        0.157,
        0.199,
        0.177,
        0.131,
        0.025,
        0.022,
        0.02,
        0.021,
        0.024,
        0.323,
        1.94,
        1.97,
        1.5,
        0.677,
        1.387,
        0.227,
    ]
    prices_tomorrow = [
        0.046,
        0.026,
        0.035,
        0.066,
        0.135,
        0.359,
        2.154,
        3.932,
        5.206,
        4.947,
        3.848,
        2.991,
        2.457,
        2.492,
        2.273,
        2.177,
        2.142,
        2.555,
        2.77,
        2.185,
        2.143,
        1.318,
        0.021,
        0.02,
    ]
    r.service.dtmodel.set_datetime(datetime(2021, 1, 1, 23, 0, 0))
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [7, 8, 9]
    await r.async_update_prices(prices_tomorrow, [])
    r.service.dtmodel.set_datetime(datetime(2021, 1, 2, 2, 0, 0))
    assert r.non_hours == [7, 8, 9]


@pytest.mark.asyncio
async def test_very_high_prices():
    MOCKHOUR = 19
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    prices = [
        2.801,
        2.265,
        2.08,
        2.265,
        3.065,
        4.704,
        5.84,
        8.691,
        9.062,
        8.53,
        8.182,
        7.348,
        6.912,
        6.909,
        7.327,
        7.597,
        7.995,
        8.43,
        9.282,
        9.987,
        8.33,
        7.795,
        5.93,
        4.052,
    ]
    prices_tomorrow = [
        3.452,
        1.311,
        0.664,
        0.664,
        0.664,
        3.37,
        4.715,
        6.25,
        6.791,
        7.457,
        7.612,
        7.467,
        6.681,
        6.367,
        6.92,
        6.871,
        6.63,
        6.804,
        7.095,
        6.63,
        5.723,
        7.321,
        5.717,
        3.386,
    ]
    r.service.dtmodel.set_hour(13)
    await r.async_update_prices(prices, prices_tomorrow)
    r.service.dtmodel.set_hour(MOCKHOUR)
    assert r.non_hours == [19, 20, 21, 10, 14, 15, 16, 17, 18]


@pytest.mark.asyncio
async def test_regular5():
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE, absolute_top_price=0, min_price=0
    )
    prices = [
        0.619,
        0.613,
        0.622,
        0.634,
        0.639,
        0.687,
        0.767,
        0.937,
        1.035,
        1.049,
        1.039,
        1.036,
        1.033,
        1.038,
        1.043,
        1.044,
        0.981,
        1.031,
        1.028,
        1.027,
        1.042,
        0.954,
        0.95,
        0.817,
    ]
    r.service.dtmodel.set_hour(0)
    await r.async_update_prices(prices)
    assert r.non_hours == [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    prices_tomorrow = [
        0.69,
        0.706,
        0.721,
        0.688,
        0.77,
        0.863,
        1.008,
        1.263,
        2.473,
        2.065,
        1.948,
        2.499,
        2.339,
        3.133,
        2.538,
        2.861,
        3.309,
        4.258,
        4.98,
        4.904,
        4.01,
        3.351,
        1.215,
        1.065,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    r.service.dtmodel.set_hour(13)
    assert r.non_hours == [13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    r.service.dtmodel.set_hour(22)
    assert r.non_hours == [22, 13, 14, 15, 16, 17, 18, 19, 20, 21]


@pytest.mark.asyncio
async def test_regular5_max_price():
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE,
        absolute_top_price=0.7,
        min_price=0,
    )
    prices = [
        0.619,
        0.613,
        0.622,
        0.634,
        0.639,
        0.687,
        0.767,
        0.937,
        1.035,
        1.049,
        1.039,
        1.036,
        1.033,
        1.038,
        1.043,
        1.044,
        0.981,
        1.031,
        1.028,
        1.027,
        1.042,
        0.954,
        0.95,
        0.817,
    ]
    await r.async_update_prices(prices)
    r.service.dtmodel.set_hour(0)
    assert r.non_hours == [
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
    ]
    prices_tomorrow = [
        0.69,
        0.706,
        0.721,
        0.688,
        0.77,
        0.863,
        1.008,
        1.263,
        2.473,
        2.065,
        1.948,
        2.499,
        2.339,
        3.133,
        2.538,
        2.861,
        3.309,
        4.258,
        4.98,
        4.904,
        4.01,
        3.351,
        1.215,
        1.065,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    r.service.dtmodel.set_hour(13)
    assert r.non_hours == [
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]


@pytest.mark.asyncio
async def test_regular6():
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE, absolute_top_price=0, min_price=0
    )
    prices = [
        0.619,
        0.613,
        0.622,
        0.634,
        0.639,
        0.687,
        0.767,
        0.937,
        1.035,
        1.049,
        1.039,
        1.036,
        1.033,
        1.038,
        1.043,
        1.044,
        0.981,
        1.031,
        1.028,
        1.027,
        1.042,
        0.954,
        0.95,
        0.817,
    ]
    await r.async_update_prices(prices)
    r.service.dtmodel.set_hour(0)
    assert r.non_hours == [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]


@pytest.mark.asyncio
async def test_regular7():
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE, absolute_top_price=0, min_price=0
    )
    prices = [
        0.69,
        0.706,
        0.721,
        0.688,
        0.77,
        0.863,
        1.008,
        1.263,
        2.473,
        2.065,
        1.948,
        2.499,
        2.339,
        3.133,
        2.538,
        2.861,
        3.309,
        4.258,
        4.98,
        4.904,
        4.01,
        3.351,
        1.215,
        1.065,
    ]
    await r.async_update_prices(prices)
    r.service.dtmodel.set_hour(0)
    assert r.non_hours == [13, 14, 15, 16, 17, 18, 19, 20, 21]


@pytest.mark.asyncio
async def test_remove_tomorrow():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(13)
    prices = [
        2.801,
        2.265,
        2.08,
        2.265,
        3.065,
        4.704,
        5.84,
        8.691,
        9.062,
        8.53,
        8.182,
        7.348,
        6.912,
        6.909,
        7.327,
        7.597,
        7.995,
        8.43,
        9.282,
        9.987,
        8.33,
        7.795,
        5.93,
        4.052,
    ]
    prices_tomorrow = [
        3.452,
        1.311,
        0.664,
        0.664,
        0.664,
        3.37,
        4.715,
        6.25,
        6.791,
        7.457,
        7.612,
        7.467,
        6.681,
        6.367,
        6.92,
        6.871,
        6.63,
        6.804,
        7.095,
        6.63,
        5.723,
        7.321,
        5.717,
        3.386,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    r.service.dtmodel.set_hour(0)
    prices = [
        3.452,
        1.311,
        0.664,
        0.664,
        0.664,
        3.37,
        4.715,
        6.25,
        6.791,
        7.457,
        7.612,
        7.467,
        6.681,
        6.367,
        6.92,
        6.871,
        6.63,
        6.804,
        7.095,
        6.63,
        5.723,
        7.321,
        5.717,
        3.386,
    ]
    await r.async_update_prices(prices)
    assert r.prices_tomorrow == []


@pytest.mark.asyncio
async def test_set_tomorrow_as_comma_string():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(13)
    prices = [
        2.801,
        2.265,
        2.08,
        2.265,
        3.065,
        4.704,
        5.84,
        8.691,
        9.062,
        8.53,
        8.182,
        7.348,
        6.912,
        6.909,
        7.327,
        7.597,
        7.995,
        8.43,
        9.282,
        9.987,
        8.33,
        7.795,
        5.93,
        4.052,
    ]
    prices_tomorrow = [
        3.452,
        1.311,
        0.664,
        0.664,
        0.664,
        3.37,
        4.715,
        6.25,
        6.791,
        7.457,
        7.612,
        7.467,
        6.681,
        6.367,
        6.92,
        6.871,
        6.63,
        6.804,
        7.095,
        6.63,
        5.723,
        7.321,
        5.717,
        3.386,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    r.service.dtmodel.set_hour(0)
    prices2 = [
        3.452,
        1.311,
        0.664,
        0.664,
        0.664,
        3.37,
        4.715,
        6.25,
        6.791,
        7.457,
        7.612,
        7.467,
        6.681,
        6.367,
        6.92,
        6.871,
        6.63,
        6.804,
        7.095,
        6.63,
        5.723,
        7.321,
        5.717,
        3.386,
    ]
    await r.async_update_prices(prices2, PRICES_BLANK)
    assert r.prices_tomorrow == []


@pytest.mark.asyncio
async def test_negative_prices_and_min_price():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0.3)
    r.service.dtmodel.set_hour(7)
    await r.async_update_prices(PNEGATIVE[0])
    assert r.non_hours == []
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(PNEGATIVE[0], PNEGATIVE[1])
    assert r.non_hours == []


@pytest.mark.asyncio
async def test_high_diff_in_interim_update():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(7)
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(P221105[0], P221105[1])
    assert r.non_hours == [17, 18, 7, 8, 9, 13]
    assert r.dynamic_caution_hours == {
        16: 0.32,
        19: 0.66,
        6: 0.7,
        10: 0.51,
        11: 0.56,
        12: 0.51,
    }


@pytest.mark.asyncio
async def test_22115_adjusted_average_today_only():
    # average today is 0.63
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(7)
    await r.async_update_prices(P221105[0])
    assert r.non_hours == [16, 17, 18]
    assert r.caution_hours == [10, 11, 12, 13, 15, 19, 20]


@pytest.mark.asyncio
async def test_22115_adjusted_average_today_only_lower():
    # average today is 0.63
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(7)
    await r.async_update_adjusted_average(0.3)
    await r.async_update_prices(P221105[0])
    assert r.non_hours == [16, 17, 18]
    assert r.caution_hours == [8, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23]


@pytest.mark.asyncio
async def test_22115_adjusted_average_today_only_raise():
    # average today is 0.63
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(7)
    await r.async_update_adjusted_average(1)
    await r.async_update_prices(P221105[0])
    assert r.non_hours == [16, 17, 18, 19]
    assert r.caution_hours == [12]


@pytest.mark.asyncio
async def test_22115_adjusted_average():
    # average today is 0.63
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(7)
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(P221105[0], P221105[1])
    assert r.non_hours == [17, 18, 7, 8, 9, 13]
    assert r.dynamic_caution_hours == {
        16: 0.32,
        19: 0.66,
        6: 0.7,
        10: 0.51,
        11: 0.56,
        12: 0.51,
    }


@pytest.mark.asyncio
async def test_22115_adjusted_average_lower():
    # average today is 0.63
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(7)
    await r.async_update_adjusted_average(0.33)
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(P221105[0], P221105[1])
    # assert r.non_hours == [17, 18, 7, 8, 9, 13]
    assert r.caution_hours == [16, 19, 5, 6, 10, 11, 12]


@pytest.mark.asyncio
async def test_22115_adjusted_average_raise():
    # average today is 0.63
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(7)
    await r.async_update_adjusted_average(1.6)
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(P221105[0], P221105[1])
    assert r.non_hours == [17, 18, 7, 8, 9, 13]
    assert r.caution_hours == [16, 6, 10, 11, 12]
    assert r.dynamic_caution_hours == {16: 0.32, 6: 0.7, 10: 0.51, 11: 0.56, 12: 0.51}


@pytest.mark.asyncio
async def test_offset_dict_1():
    r = h()
    await r.async_update_prices(P221105[0])
    _tod1 = r.offsets.get("today")
    assert _tod1 == {
        0: -1.0,
        1: -0.96,
        2: -0.92,
        3: -0.88,
        4: -0.84,
        5: -0.81,
        6: -0.75,
        7: -0.67,
        8: -0.58,
        9: -0.39,
        10: -0.29,
        11: -0.22,
        12: -0.13,
        13: -0.22,
        14: -0.32,
        15: -0.23,
        16: 2.74,
        17: 3.85,
        18: 3.51,
        19: 0.91,
        20: -0.29,
        21: -0.44,
        22: -0.51,
        23: -0.54,
    }
    _tom1 = r.offsets.get("tomorrow")
    assert _tom1 == {}
    await r.async_update_prices(P221105[0], P221105[1])
    _tod = r.offsets.get("today")
    _tom = r.offsets.get("tomorrow")
    assert _tod == {
        0: -0.89,
        1: -0.89,
        2: -0.86,
        3: -0.87,
        4: -0.86,
        5: -0.75,
        6: -0.02,
        7: 1.33,
        8: 1.38,
        9: 0.88,
        10: 0.55,
        11: 0.39,
        12: 0.57,
        13: 0.87,
        14: 1.36,
        15: 0.77,
        16: 0.77,
        17: 1.15,
        18: 0.82,
        19: 0.54,
        20: 0.26,
        21: -0.25,
        22: -0.96,
        23: -1.0,
    }
    assert _tom == {
        0: -0.89,
        1: -0.89,
        2: -0.86,
        3: -0.87,
        4: -0.86,
        5: -0.75,
        6: -0.02,
        7: 1.33,
        8: 1.38,
        9: 0.88,
        10: 0.55,
        11: 0.39,
        12: 0.57,
        13: 0.87,
        14: 1.36,
        15: 0.77,
        16: 0.77,
        17: 1.15,
        18: 0.82,
        19: 0.54,
        20: 0.26,
        21: -0.25,
        22: -0.96,
        23: -1.0,
    }


@pytest.mark.asyncio
async def test_offset_dict_2():
    """Same stdev as test_offset_dict_1 but more expensive overall."""
    r = h()
    prices = [
        5.139,
        5.157,
        5.176,
        5.196,
        5.219,
        5.232,
        5.263,
        5.3,
        5.345,
        5.436,
        5.488,
        5.523,
        5.565,
        5.521,
        5.475,
        5.515,
        6.972,
        7.521,
        7.351,
        6.074,
        5.488,
        5.416,
        5.378,
        5.364,
    ]
    await r.async_update_prices(prices)
    assert r.offsets == {
        "today": {
            0: -1.0,
            1: -0.96,
            2: -0.92,
            3: -0.88,
            4: -0.84,
            5: -0.81,
            6: -0.75,
            7: -0.67,
            8: -0.58,
            9: -0.39,
            10: -0.29,
            11: -0.22,
            12: -0.13,
            13: -0.22,
            14: -0.32,
            15: -0.23,
            16: 2.74,
            17: 3.85,
            18: 3.51,
            19: 0.91,
            20: -0.29,
            21: -0.44,
            22: -0.51,
            23: -0.54,
        },
        "tomorrow": {},
    }
    prices_tomorrow = [
        5.47,
        5.475,
        5.499,
        5.489,
        5.499,
        5.616,
        6.341,
        7.69,
        7.74,
        7.237,
        6.914,
        6.746,
        6.926,
        7.227,
        7.719,
        7.853,
        7.855,
        8.416,
        7.928,
        7.519,
        7.105,
        6.344,
        5.287,
        5.232,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.offsets == {
        "today": {
            0: -1.0,
            1: -0.96,
            2: -0.92,
            3: -0.88,
            4: -0.84,
            5: -0.81,
            6: -0.75,
            7: -0.67,
            8: -0.58,
            9: -0.39,
            10: -0.29,
            11: -0.22,
            12: -0.13,
            13: -0.22,
            14: -0.88,
            15: -0.83,
            16: 0.78,
            17: 1.39,
            18: 1.2,
            19: -0.21,
            20: -0.86,
            21: -0.94,
            22: -0.98,
            23: -1.0,
        },
        "tomorrow": {
            0: -0.88,
            1: -0.88,
            2: -0.85,
            3: -0.86,
            4: -0.85,
            5: -0.72,
            6: 0.08,
            7: 1.57,
            8: 1.63,
            9: 1.07,
            10: 0.72,
            11: 0.53,
            12: 0.73,
            13: 1.06,
            14: 0.68,
            15: 0.77,
            16: 0.77,
            17: 1.15,
            18: 0.82,
            19: 0.54,
            20: 0.26,
            21: -0.25,
            22: -0.96,
            23: -1.0,
        },
    }


@pytest.mark.asyncio
async def test_22127_1():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(7)
    prices = [
        1.918,
        1.795,
        1.654,
        1.348,
        1.348,
        1.432,
        1.695,
        1.797,
        1.837,
        1.993,
        2.032,
        2.163,
        2.113,
        2.059,
        2.131,
        2.142,
        2.247,
        2.366,
        2.37,
        2.213,
        2.067,
        1.724,
        1.334,
        1.136,
    ]
    await r.async_update_prices(prices)
    assert r.non_hours == [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    assert r.caution_hours == [7, 8, 21]


@pytest.mark.asyncio
async def test_22127_1_adjusted_average():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(7)
    await r.async_update_adjusted_average(2.8)
    prices = [
        1.918,
        1.795,
        1.654,
        1.348,
        1.348,
        1.432,
        1.695,
        1.797,
        1.837,
        1.993,
        2.032,
        2.163,
        2.113,
        2.059,
        2.131,
        2.142,
        2.247,
        2.366,
        2.37,
        2.213,
        2.067,
        1.724,
        1.334,
        1.136,
    ]
    await r.async_update_prices(prices)
    assert r.non_hours == [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    assert r.caution_hours == []


@pytest.mark.asyncio
async def test_22127_2_adjusted_average():
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE, absolute_top_price=0, min_price=0
    )
    # avg today is 1.87
    r.service.dtmodel.set_hour(0)
    await r.async_update_adjusted_average(2.8)
    prices = [
        1.918,
        1.795,
        1.654,
        1.348,
        1.348,
        1.432,
        1.695,
        1.797,
        1.837,
        1.993,
        2.032,
        2.163,
        2.113,
        2.059,
        2.131,
        2.142,
        2.247,
        2.366,
        2.37,
        2.213,
        2.067,
        1.724,
        1.334,
        1.136,
    ]
    await r.async_update_prices(prices)
    assert r.non_hours == [0, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    r.service.dtmodel.set_hour(22)
    prices_tomorrow = [
        1.71,
        1.714,
        1.661,
        1.566,
        1.578,
        1.628,
        1.994,
        2.468,
        2.767,
        2.804,
        3.091,
        3.162,
        3.151,
        3.151,
        3.15,
        3.158,
        3.329,
        3.39,
        3.27,
        2.98,
        2.743,
        2.578,
        2.409,
        1.918,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    assert r.dynamic_caution_hours == {}


@pytest.mark.asyncio
async def test_22128_1():
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE, absolute_top_price=0, min_price=0
    )
    # avg today is 1.87
    r.service.dtmodel.set_hour(0)
    prices = [
        1.713,
        1.716,
        1.663,
        1.568,
        1.58,
        1.631,
        1.996,
        2.471,
        2.771,
        2.808,
        3.095,
        3.166,
        3.155,
        3.155,
        3.154,
        3.162,
        3.333,
        3.394,
        3.275,
        2.984,
        2.747,
        2.582,
        2.412,
        1.92,
    ]
    await r.async_update_prices(prices)
    assert r.non_hours == [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    r.service.dtmodel.set_hour(14)
    prices_tomorrow = [
        2.851,
        2.787,
        2.855,
        2.853,
        2.855,
        3.02,
        3.532,
        5.259,
        6.032,
        6.057,
        6.065,
        5.924,
        5.686,
        5.77,
        6.071,
        6.13,
        6.257,
        6.815,
        6.621,
        6.157,
        5.31,
        4.481,
        3.951,
        3.568,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [7, 8, 9, 10, 11, 12, 13]
    assert r.dynamic_caution_hours == {16: 0.47, 17: 0.46, 18: 0.48, 6: 0.44}


@pytest.mark.asyncio
async def test_22128_1_adjusted_average():
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE, absolute_top_price=0, min_price=0
    )
    # avg today is 1.87
    r.service.dtmodel.set_hour(0)
    await r.async_update_adjusted_average(2.7)
    prices = [
        1.713,
        1.716,
        1.663,
        1.568,
        1.58,
        1.631,
        1.996,
        2.471,
        2.771,
        2.808,
        3.095,
        3.166,
        3.155,
        3.155,
        3.154,
        3.162,
        3.333,
        3.394,
        3.275,
        2.984,
        2.747,
        2.582,
        2.412,
        1.92,
    ]
    await r.async_update_prices(prices)
    assert r.non_hours == [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    r.service.dtmodel.set_hour(14)
    prices_tomorrow = [
        2.851,
        2.787,
        2.855,
        2.853,
        2.855,
        3.02,
        3.532,
        5.259,
        6.032,
        6.057,
        6.065,
        5.924,
        5.686,
        5.77,
        6.071,
        6.13,
        6.257,
        6.815,
        6.621,
        6.157,
        5.31,
        4.481,
        3.951,
        3.568,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [
        14,
        15,
        16,
        17,
        18,
        19,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
    ]
    # assert r.dynamic_caution_hours == {
    #     14: 0.5,
    #     15: 0.5,
    #     16: 0.47,
    #     17: 0.46,
    #     18: 0.48,
    #     19: 0.54,
    #     0: 0.56,
    #     2: 0.56,
    #     3: 0.56,
    #     4: 0.56,
    #     5: 0.53,
    #     6: 0.44,
    # }


@pytest.mark.asyncio
async def test_same_price_same_offset():
    """should be equal offset for equal prices over the days due to interim-day update"""
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE, absolute_top_price=0, min_price=0
    )
    r.service.dtmodel.set_hour(0)
    prices = [
        1.713,
        1.716,
        1.663,
        1.568,
        1.58,
        1.631,
        1.996,
        2.471,
        2.771,
        2.808,
        3.095,
        3.166,
        3.155,
        3.155,
        3.154,
        3.162,
        3.333,
        3.394,
        3.275,
        2.984,
        2.747,
        4.32,
        3.14,
        2.853,
    ]
    r.service.dtmodel.set_hour(14)
    prices_tomorrow = [
        2.853,
        3.14,
        4.32,
        2.853,
        2.855,
        3.02,
        3.532,
        5.259,
        6.032,
        6.057,
        6.065,
        5.924,
        5.686,
        5.77,
        6.071,
        6.13,
        6.257,
        6.815,
        6.621,
        6.157,
        5.31,
        4.481,
        3.951,
        3.568,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    print(r.offsets)
    assert r.offsets["today"][23] == r.offsets["tomorrow"][0]
    assert r.offsets["today"][22] == r.offsets["tomorrow"][1]
    assert r.offsets["today"][21] == r.offsets["tomorrow"][2]


@pytest.mark.asyncio
async def test_offset_total():
    """should be close to zero offset on average"""
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE, absolute_top_price=0, min_price=0
    )
    r.service.dtmodel.set_hour(0)
    for price in MOCKPRICELIST:
        prices = price
        await r.async_update_prices(prices)
        assert round(stat.mean(r.offsets["today"].values()), 2) == 0


@pytest.mark.asyncio
async def test_not_too_shallow_caution_hours():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(0)
    prices = [
        1.713,
        1.716,
        1.663,
        1.568,
        1.58,
        1.631,
        1.996,
        2.471,
        2.771,
        2.808,
        3.095,
        3.166,
        3.155,
        3.155,
        3.154,
        3.162,
        3.333,
        3.394,
        3.275,
        2.984,
        2.747,
        4.32,
        3.14,
        2.853,
    ]
    await r.async_update_prices(prices)
    val = [c for c in r.dynamic_caution_hours.values() if c < 0.3]
    r.service.dtmodel.set_hour(14)
    prices_tomorrow = [
        2.853,
        3.14,
        4.32,
        2.853,
        2.855,
        3.02,
        3.532,
        5.259,
        6.032,
        6.057,
        6.065,
        5.924,
        5.686,
        5.77,
        6.071,
        6.13,
        6.257,
        6.815,
        6.621,
        6.157,
        5.31,
        4.481,
        3.951,
        3.568,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    val2 = [c for c in r.dynamic_caution_hours.values() if c < 0.3]
    assert len(val) == 0
    assert len(val2) == 0


@pytest.mark.asyncio
async def test_charge_below_average_today_only():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(0)
    _avg = 0
    for price in MOCKPRICELIST:
        prices = price
        await r.async_update_prices(prices)
        _avg = round(stat.mean(price), 2)
        ret = await r.async_get_average_kwh_price()
        _measure = round(ret[0], 2) if ret[0] else 0
        try:
            assert 0 < _measure <= _avg
        except AssertionError:
            raise AssertionError(f"avg: {_avg}, ret: {_measure}")


@pytest.mark.asyncio
async def test_charge_price_fixed_today_only():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(0)
    prices = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    await r.async_update_prices(prices)
    ret = await r.async_get_average_kwh_price()
    assert ret[0] == 1


@pytest.mark.asyncio
async def test_charge_price_fixed_today_tomorrow():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(13)
    prices = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1]
    prices_tomorrow = [
        1,
        1,
        1,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    ret = await r.async_get_average_kwh_price()
    assert ret[0] == 1


@pytest.mark.asyncio
async def test_charge_below_average_today_and_tomorrow():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(14)
    _avg = 0
    for price in MOCKPRICELIST:
        for price2 in MOCKPRICELIST:
            if price == price2:
                continue
            prices = price
            prices_tomorrow = price2
            await r.async_update_prices(prices, prices_tomorrow)
            total = price[14::] + price2[0:14]
            _avg = round(stat.mean(total), 2)
            ret = await r.async_get_average_kwh_price()
            assert 0 < ret[0] <= _avg
            print(f"{_avg}; {ret}; {round((ret[0]/_avg)-1,2)}")
    # assert 1 < 0


@pytest.mark.asyncio
async def test_charge_below_average_today_and_tomorrow_compare_to_mediancharge():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    r.service.dtmodel.set_hour(14)
    _avg = 0
    for price in MOCKPRICELIST:
        for price2 in MOCKPRICELIST:
            if price == price2:
                continue
            prices = price
            prices_tomorrow = price2
            await r.async_update_prices(prices, prices_tomorrow)
            total = price[14::] + price2[0:14]
            legacy_charge = stat.mean(
                [h for h in price[14::] if h < stat.mean(price)]
                + [h for h in price2[0:14:] if h < stat.mean(price2)]
            )
            _avg = round(stat.mean(total), 2)
            # assert await r.async_get_average_kwh_price() <= round(legacy_charge,1)
            # print(f"{_avg}; {await r.async_get_average_kwh_price()}; {legacy_charge}")
    # assert 1 < 0


@pytest.mark.asyncio
async def test_charge_below_average_today_only_compare_to_mediancharge():
    # for intermediate and aggressive it always works below mediancharge, for suave no because of caution-hours.
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE, absolute_top_price=0, min_price=0
    )
    r.service.dtmodel.set_hour(0)
    for price in MOCKPRICELIST:
        prices = price
        await r.async_update_prices(prices)
        legacy_charge = stat.mean([h for h in price if h < stat.mean(price)])
        _avg = round(stat.mean(price), 2)


@pytest.mark.asyncio
async def test_weird_pricelist():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=0, min_price=0)
    prices = [
        0.028,
        0.019,
        0.001,
        0.001,
        0.001,
        0.001,
        0.001,
        0.007,
        0.028,
        0.043,
        0.062,
        0.084,
        0.084,
        0.079,
        0.246,
        0.335,
        0.508,
        0.64,
        0.754,
        0.745,
        0.668,
        0.621,
        0.639,
        0.486,
    ]
    prices_tomorrow = [
        0.805,
        0.718,
        0.735,
        0.614,
        0.696,
        0.983,
        1.425,
        1.921,
        2.029,
        2.044,
        2.024,
        1.992,
        2.007,
        1.998,
        2.06,
        2.159,
        2.264,
        2.363,
        2.429,
        2.286,
        2.127,
        1.969,
        1.83,
        1.641,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    r.service.dtmodel.set_hour(20)
    assert len(r.offsets["today"])
    assert len(r.offsets["tomorrow"])


@pytest.mark.asyncio
async def test_cheapest_cautionhour_in_nonhours():
    """
    in frontend, 9 and 11 were non-hours but 10 was cautionhour with the below settings.
    possibly because of midnight-recalculation (ie a reboot might fix)
    """
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE,
        absolute_top_price=5.5,
        min_price=0,
    )
    prices = [
        0.342,
        0.13,
        0.127,
        0.058,
        0.078,
        0.139,
        0.126,
        0.23,
        0.379,
        0.407,
        0.493,
        0.658,
        0.658,
        0.685,
        0.768,
        0.888,
        0.925,
        0.968,
        0.978,
        0.918,
        0.853,
        0.803,
        0.7,
        0.648,
    ]
    await r.async_update_adjusted_average(1.34)
    await r.async_update_prices(prices)
    r.service.dtmodel.set_hour(0)
    assert r.non_hours == [16, 17, 18, 19]
    assert r.dynamic_caution_hours == {}
    assert r.model.options.absolute_top_price == 5.5


@pytest.mark.asyncio
async def test_230108():
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE,
        absolute_top_price=5.5,
        min_price=0,
    )
    prices = [
        0.342,
        0.13,
        0.127,
        0.058,
        0.078,
        0.139,
        0.126,
        0.23,
        0.379,
        0.407,
        0.493,
        0.658,
        0.658,
        0.685,
        0.768,
        0.888,
        0.925,
        0.968,
        0.978,
        0.918,
        0.853,
        0.803,
        0.7,
        0.648,
    ]
    r.service.dtmodel.set_hour(12)
    await r.async_update_prices(prices)
    await r.async_update_adjusted_average(1.34)
    assert r.non_hours == [15, 16, 17, 18, 19]


@pytest.mark.asyncio
async def test_cautionhourtypes():
    nonhours = {
        CautionHourType.SUAVE.value: [14, 15, 16, 17, 18, 20, 21],
        CautionHourType.INTERMEDIATE.value: [
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            20,
            21,
            22,
            23,
        ],
        CautionHourType.AGGRESSIVE.value: [12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23],
        CautionHourType.SCROOGE.value: [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
    }

    cautionhours = {
        CautionHourType.SUAVE.value: {12: 0.38, 13: 0.34, 19: 0.54, 22: 0.32, 23: 0.39},
        CautionHourType.INTERMEDIATE.value: {19: 0.49},
        CautionHourType.AGGRESSIVE.value: {19: 0.47},
        CautionHourType.SCROOGE.value: {},
    }
    for c in CautionHourType:
        r = h(cautionhour_type=c, absolute_top_price=3, min_price=0)
        assert r.model.options.cautionhour_type == VALUES_CONVERSION[c.value]
        prices = [
            0.342,
            0.13,
            0.127,
            0.058,
            0.078,
            0.139,
            0.126,
            0.23,
            0.379,
            0.407,
            0.493,
            0.658,
            0.658,
            0.685,
            0.768,
            0.888,
            0.925,
            0.968,
            0.978,
            0.518,
            0.853,
            0.803,
            0.7,
            0.648,
        ]
        await r.async_update_prices(prices)
        r.service.dtmodel.set_hour(12)
        assert r.non_hours == nonhours[c.value]
        assert r.dynamic_caution_hours == cautionhours[c.value]


@pytest.mark.asyncio
async def test_230205_cautionhourtypes():
    nonhours = {
        CautionHourType.SUAVE.value: [6, 7, 8, 9, 10, 11, 12],
        CautionHourType.INTERMEDIATE.value: [17, 6, 7, 8, 9, 10, 11, 12, 13],
        CautionHourType.AGGRESSIVE.value: [17, 6, 7, 8, 9, 10, 11, 12, 13],
        CautionHourType.SCROOGE.value: [
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
        ],
    }
    cautionhours = {
        CautionHourType.SUAVE.value: {
            15: 0.54,
            16: 0.51,
            17: 0.41,
            18: 0.45,
            19: 0.46,
            20: 0.51,
            21: 0.51,
            22: 0.51,
            4: 0.51,
            5: 0.47,
            13: 0.29,
            14: 0.46,
        },
        CautionHourType.INTERMEDIATE.value: {
            15: 0.49,
            16: 0.46,
            18: 0.41,
            19: 0.42,
            20: 0.46,
            21: 0.46,
            22: 0.46,
            4: 0.46,
            5: 0.43,
            14: 0.42,
        },
        CautionHourType.AGGRESSIVE.value: {
            15: 0.47,
            16: 0.44,
            18: 0.39,
            19: 0.4,
            20: 0.44,
            21: 0.44,
            22: 0.44,
            4: 0.44,
            5: 0.41,
            14: 0.4,
        },
        CautionHourType.SCROOGE.value: {},
    }
    for c in CautionHourType:
        r = h(cautionhour_type=c, absolute_top_price=3, min_price=0)
        assert r.model.options.cautionhour_type == VALUES_CONVERSION[c.value]
        await r.async_update_adjusted_average(1.38)
        await r.async_update_prices(P230205[0], P230205[1])
        r.service.dtmodel.set_hour(15)
        assert r.non_hours == nonhours[c.value]
        assert r.dynamic_caution_hours == cautionhours[c.value]
        del r


@pytest.mark.asyncio
async def test_230205_interimday():
    r = h(
        cautionhour_type=CautionHourType.INTERMEDIATE.value,
        absolute_top_price=3,
        min_price=0,
    )
    await r.async_update_prices(P230205[0], P230205[1])
    await r.async_update_adjusted_average(1.38)
    r.service.dtmodel.set_hour(13)
    assert r.non_hours == [13, 17, 6, 7, 8, 9, 10, 11, 12]
    assert r.caution_hours == [14, 15, 16, 18, 19, 20, 21, 22, 4, 5]
    r.service.dtmodel.set_hour(14)
    assert r.non_hours == [17, 6, 7, 8, 9, 10, 11, 12, 13]
    assert r.caution_hours == [14, 15, 16, 18, 19, 20, 21, 22, 4, 5]


@pytest.mark.asyncio
async def test_230208():
    r = h(
        cautionhour_type=CautionHourType.AGGRESSIVE.value,
        absolute_top_price=3,
        min_price=0.0,
    )
    prices = [
        1.138,
        1.112,
        1.019,
        0.925,
        0.925,
        0.937,
        1.499,
        1.7,
        1.708,
        1.678,
        1.339,
        0.925,
        0.593,
        0.485,
        0.416,
        0.412,
        0.412,
        0.41,
        0.404,
        0.409,
        0.362,
        0.306,
        0.282,
        0.198,
    ]
    prices_tomorrow = [
        0.17,
        0.142,
        0.108,
        0.104,
        0.168,
        0.234,
        0.29,
        0.355,
        0.402,
        0.412,
        0.417,
        0.408,
        0.395,
        0.366,
        0.357,
        0.362,
        0.361,
        0.382,
        0.371,
        0.342,
        0.332,
        0.317,
        0.303,
        0.284,
    ]
    await r.async_update_prices(prices, prices_tomorrow)
    r.service.dtmodel.set_hour(13)
    assert r.non_hours == [13, 14, 15, 16, 17, 18, 19, 20, 7, 8, 9, 10, 11, 12]
    r.service.dtmodel.set_hour(14)
    assert r.non_hours == [14, 15, 16, 17, 18, 19, 20, 7, 8, 9, 10, 11, 12, 13]


@pytest.mark.asyncio
async def test_230313_issue_72():
    r = h(
        cautionhour_type=CautionHourType.AGGRESSIVE.value,
        absolute_top_price=3,
        min_price=0.0,
    )
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(P230313[0], P230313[1])
    await r.async_update_adjusted_average(1.44)
    await r.async_update_top_price(1.45)

    assert r.non_hours == [7, 8, 9, 10]
    ret = await r.async_get_average_kwh_price()
    assert ret[0] == 0.47


@pytest.mark.asyncio
async def test_230313_issue_72_scrooge():
    r = h(cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=3, min_price=0.0)
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(P230313[0], P230313[1])
    await r.async_update_adjusted_average(1.44)
    await r.async_update_top_price(1.45)
    assert r.non_hours == [14, 16, 17, 18, 19, 20, 21, 22, 6, 7, 8, 9, 10, 11, 12, 13]
    # assert await r.async_get_average_kwh_price() == 0.19


@pytest.mark.asyncio
async def test_230314_block_nocturnal():
    r = h(
        cautionhour_type=CautionHourType.AGGRESSIVE,
        absolute_top_price=3,
        min_price=0.0,
        blocknocturnal=True,
    )
    prices = [
        0.709,
        0.557,
        0.492,
        0.433,
        0.48,
        0.486,
        0.548,
        1.106,
        1.136,
        0.604,
        0.445,
        0.439,
        0.474,
        0.481,
        0.464,
        0.449,
        0.45,
        0.674,
        0.747,
        0.695,
        0.624,
        0.6,
        0.492,
        0.332,
    ]
    prices_tomorrow = [
        0.137,
        0.065,
        0.06,
        0.035,
        0.066,
        0.386,
        0.61,
        0.994,
        1.325,
        1.164,
        1.056,
        0.872,
        0.762,
        0.853,
        0.937,
        0.856,
        1.128,
        1.43,
        1.489,
        1.489,
        1.42,
        0.913,
        0.778,
        0.724,
    ]
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(prices, prices_tomorrow)
    await r.async_update_adjusted_average(1.44)
    await r.async_update_top_price(1.45)
    assert r.non_hours == [23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@pytest.mark.asyncio
async def test_230317_today_only():
    r = h(cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=3, min_price=0.0)
    prices = [
        0.475,
        0.457,
        0.442,
        0.42,
        0.414,
        0.415,
        0.44,
        0.466,
        0.47,
        0.459,
        0.46,
        0.456,
        0.455,
        0.452,
        0.453,
        0.422,
        0.417,
        0.411,
        0.405,
        0.372,
        0.339,
        0.327,
        0.313,
        0.257,
    ]
    await r.async_update_prices(prices)
    await r.async_update_adjusted_average(0.87)
    await r.async_update_top_price(1.33)
    r.service.dtmodel.set_hour(9)
    assert r.non_hours == [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]


@pytest.mark.asyncio
async def test_230317_today_tomorrow():
    r = h(cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=2, min_price=0.0)
    prices = [
        0.475,
        0.457,
        0.442,
        0.42,
        0.414,
        0.415,
        0.44,
        0.466,
        0.47,
        0.459,
        0.46,
        0.456,
        0.455,
        0.452,
        0.453,
        0.422,
        0.417,
        0.411,
        0.405,
        0.372,
        0.339,
        0.327,
        0.313,
        0.257,
    ]
    prices_tomorrow = [
        0.057,
        0.057,
        0.057,
        0.139,
        0.24,
        0.293,
        0.3,
        0.32,
        0.401,
        0.417,
        0.456,
        0.457,
        0.452,
        0.445,
        0.424,
        0.437,
        0.466,
        0.766,
        1.35,
        0.767,
        0.484,
        0.487,
        0.471,
        0.464,
    ]
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(prices, prices_tomorrow)
    await r.async_update_adjusted_average(0.87)
    await r.async_update_top_price(1.33)
    assert r.non_hours == [14, 15, 16, 17, 18, 19, 20, 21, 22, 5, 6, 7, 8, 9, 12, 13]
    r.service.dtmodel.set_hour(20)
    assert r.non_hours == [20, 21, 22, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19]
    assert r.caution_hours == []
    assert r.dynamic_caution_hours == {}


@pytest.mark.asyncio
async def test_230318_today_tomorrow():
    r = h(cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=3, min_price=0.0)
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(1.28)
    r.service.dtmodel.set_hour(13)
    assert r.service.dtmodel.hour == 13
    await r.async_update_prices(P230318[0], P230318[1])
    assert r.non_hours == [17, 18, 19, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


@pytest.mark.asyncio
async def test_230319_today_tomorrow_scrooge():
    r = h(cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=3, min_price=0.0)
    prices = [
        0.505,
        0.517,
        0.544,
        0.558,
        0.588,
        0.613,
        0.637,
        0.689,
        0.84,
        1.067,
        1.014,
        0.939,
        0.77,
        0.63,
        0.699,
        0.77,
        1.106,
        1.383,
        1.399,
        0.749,
        0.469,
        0.442,
        0.396,
        0.349,
    ]
    prices_tomorrow = [
        0.363,
        0.361,
        0.369,
        0.402,
        0.469,
        0.546,
        0.574,
        1.445,
        1.461,
        1.45,
        1.446,
        1.419,
        1.355,
        1.333,
        1.333,
        1.355,
        1.393,
        1.467,
        1.523,
        1.684,
        1.512,
        1.498,
        1.448,
        1.107,
    ]
    await r.async_update_adjusted_average(0.8)
    await r.async_update_top_price(1.25)
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [14, 15, 16, 17, 18, 19, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    assert r.caution_hours == []


@pytest.mark.asyncio
async def test_230322_over_night_scrooge():
    r = h(cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=3, min_price=0.0)
    prices = [
        0.505,
        0.517,
        0.544,
        0.558,
        0.588,
        0.613,
        0.637,
        0.689,
        0.84,
        1.067,
        1.014,
        0.939,
        0.77,
        0.63,
        0.699,
        0.77,
        1.106,
        1.383,
        1.399,
        0.749,
        0.469,
        0.442,
        0.396,
        0.349,
    ]
    prices_tomorrow = [
        0.363,
        0.361,
        0.369,
        0.402,
        0.469,
        0.546,
        0.574,
        1.445,
        1.461,
        1.45,
        1.446,
        1.419,
        1.355,
        1.333,
        1.333,
        1.355,
        1.393,
        1.467,
        1.523,
        1.684,
        1.512,
        1.498,
        1.448,
        1.107,
    ]
    await r.async_update_adjusted_average(0.8)
    await r.async_update_top_price(1.25)
    r.service.dtmodel.set_datetime(datetime(2023, 3, 22, 14, 0, 0))
    await r.async_update_prices(prices, prices_tomorrow)
    assert r.non_hours == [14, 15, 16, 17, 18, 19, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    r.service.dtmodel.set_datetime(datetime(2023, 3, 23, 0, 0, 0))
    await r.async_update_prices(prices_tomorrow)
    _non_hours = r.non_hours
    # assert len(r.offsets.get("today")) == 24
    # assert len(r.offsets.get("tomorrow")) == 0
    assert _non_hours == [
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
    ]
    r.service.dtmodel.set_hour(1)
    # nothing should change here.
    await r.async_update_prices(prices_tomorrow, [])
    assert r.non_hours == _non_hours
    assert len(r.offsets.get("today")) == 24
    assert len(r.offsets.get("tomorrow")) == 0
    assert r.service.preserve_interim is True
    await r.async_update_prices(prices_tomorrow, prices)
    assert r.service.preserve_interim is True
    assert r.non_hours != _non_hours


@pytest.mark.asyncio
async def test_adjust_tomorrows_top_price_1():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=3, min_price=0.0)
    prices = [
        0.505,
        0.517,
        0.544,
        0.558,
        0.588,
        0.613,
        0.637,
        0.689,
        0.84,
        1.067,
        1.014,
        0.939,
        0.77,
        0.63,
        0.699,
        0.77,
        1.106,
        1.383,
        1.399,
        0.749,
        0.469,
        0.442,
        0.396,
        0.349,
    ]
    prices_tomorrow = [
        0.363,
        0.361,
        0.369,
        0.402,
        0.469,
        0.546,
        0.574,
        1.445,
        1.461,
        1.45,
        1.446,
        1.419,
        1.355,
        1.333,
        1.333,
        1.355,
        1.393,
        1.467,
        1.523,
        1.684,
        1.512,
        1.498,
        1.448,
        1.107,
    ]
    await r.async_update_adjusted_average(0.8)
    r.service.dtmodel.set_date(date(2023, 1, 1))
    assert r.model.options.top_price_type == TopPriceType.Absolute
    await r.async_update_top_price(0.4)
    assert r.model.options.top_price_type == TopPriceType.Dynamic
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(prices, prices_tomorrow)
    assert len(r.non_hours) == 19


@pytest.mark.asyncio
async def test_adjust_tomorrows_top_price_5():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=3, min_price=0.0)
    prices = [
        0.505,
        0.517,
        0.544,
        0.558,
        0.588,
        0.613,
        0.637,
        0.689,
        0.84,
        1.067,
        1.014,
        0.939,
        0.77,
        0.63,
        0.699,
        0.77,
        1.106,
        1.383,
        1.399,
        0.749,
        0.469,
        0.442,
        0.396,
        0.349,
    ]
    prices_tomorrow = [
        0.363,
        0.361,
        0.369,
        0.402,
        0.469,
        0.546,
        0.574,
        1.445,
        1.461,
        1.45,
        1.446,
        1.419,
        1.355,
        1.333,
        1.333,
        1.355,
        1.393,
        1.467,
        1.523,
        1.684,
        1.512,
        1.498,
        1.448,
        1.107,
    ]
    await r.async_update_adjusted_average(0.8)
    r.service.dtmodel.set_date(date(2023, 1, 5))
    assert r.model.options.top_price_type == TopPriceType.Absolute
    await r.async_update_top_price(0.4)
    assert r.model.options.top_price_type == TopPriceType.Dynamic
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(prices, prices_tomorrow)
    assert len(r.non_hours) == 19


@pytest.mark.asyncio
async def test_adjust_tomorrows_top_price_10():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=10, min_price=0.0)
    prices = [
        0.505,
        0.517,
        0.544,
        0.558,
        0.588,
        0.613,
        0.637,
        0.689,
        0.84,
        1.067,
        1.014,
        0.939,
        0.77,
        0.63,
        0.699,
        0.77,
        1.106,
        1.383,
        1.399,
        0.749,
        0.469,
        0.442,
        0.396,
        0.349,
    ]
    prices_tomorrow = [
        0.363,
        0.361,
        0.369,
        0.402,
        0.469,
        0.546,
        0.574,
        1.445,
        1.461,
        1.45,
        1.446,
        1.419,
        1.355,
        1.333,
        1.333,
        1.355,
        1.393,
        1.467,
        1.523,
        1.684,
        1.512,
        1.498,
        1.448,
        1.107,
    ]
    await r.async_update_adjusted_average(0.8)
    r.service.dtmodel.set_date(date(2023, 1, 10))
    assert r.model.options.top_price_type == TopPriceType.Absolute
    await r.async_update_top_price(0.6)
    assert r.model.options.top_price_type == TopPriceType.Dynamic
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(prices, prices_tomorrow)
    assert len(r.non_hours) == 13


@pytest.mark.asyncio
async def test_adjust_tomorrows_top_price_15():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    prices = [
        0.505,
        0.517,
        0.544,
        0.558,
        0.588,
        0.613,
        0.637,
        0.689,
        0.84,
        1.067,
        1.014,
        0.939,
        0.77,
        0.63,
        0.699,
        0.77,
        1.106,
        1.383,
        1.399,
        0.749,
        0.469,
        0.442,
        0.396,
        0.349,
    ]
    prices_tomorrow = [
        0.363,
        0.361,
        0.369,
        0.402,
        0.469,
        0.546,
        0.574,
        1.445,
        1.461,
        1.45,
        1.446,
        1.419,
        1.355,
        1.333,
        1.333,
        1.355,
        1.393,
        1.467,
        1.523,
        1.684,
        1.512,
        1.498,
        1.448,
        1.107,
    ]
    await r.async_update_adjusted_average(0.8)
    r.service.dtmodel.set_date(date(2023, 1, 15))
    assert r.model.options.top_price_type == TopPriceType.Absolute
    await r.async_update_top_price(4)
    assert r.model.options.top_price_type == TopPriceType.Dynamic
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(prices, prices_tomorrow)
    assert len(r.non_hours) == 10


@pytest.mark.asyncio
async def test_adjust_tomorrows_top_price_25():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    prices = [
        0.505,
        0.517,
        0.544,
        0.558,
        0.588,
        0.613,
        0.637,
        0.689,
        0.84,
        1.067,
        1.014,
        0.939,
        0.77,
        0.63,
        0.699,
        0.77,
        1.106,
        1.383,
        1.399,
        0.749,
        0.469,
        0.442,
        0.396,
        0.349,
    ]
    prices_tomorrow = [
        0.363,
        0.361,
        0.369,
        0.402,
        0.469,
        0.546,
        0.574,
        1.445,
        1.461,
        1.45,
        1.446,
        1.419,
        1.355,
        1.333,
        1.333,
        1.355,
        1.393,
        1.467,
        1.523,
        1.684,
        1.512,
        1.498,
        1.448,
        1.107,
    ]
    await r.async_update_adjusted_average(0.8)
    r.service.dtmodel.set_date(date(2023, 1, 29))
    assert r.model.options.top_price_type == TopPriceType.Absolute
    await r.async_update_top_price(0.7)
    assert r.model.options.top_price_type == TopPriceType.Dynamic
    r.service.dtmodel.set_hour(14)
    await r.async_update_prices(prices, prices_tomorrow)
    assert len(r.non_hours) == 12


@pytest.mark.asyncio
async def test_230412():
    r = h(
        cautionhour_type=CautionHourType.AGGRESSIVE,
        absolute_top_price=30,
        min_price=0.0,
    )

    await r.async_update_adjusted_average(0.77)
    r.service.dtmodel.set_date(date(2023, 1, 12))
    assert r.model.options.top_price_type == TopPriceType.Absolute
    await r.async_update_top_price(0.97)
    assert r.model.options.top_price_type == TopPriceType.Dynamic
    r.service.dtmodel.set_hour(22)
    await r.async_update_prices(P230412[0], P230412[1])
    assert r.non_hours == []
    assert r.dynamic_caution_hours == {}


@pytest.mark.asyncio
async def test_negative_price_230430():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=3, min_price=0.0)
    prices = [
        0.45,
        0.45,
        0.43,
        0.43,
        0.43,
        0.42,
        0.43,
        0.45,
        0.5,
        0.48,
        0.43,
        0.14,
        0.07,
        0.05,
        0.04,
        0.07,
        0.25,
        0.51,
        0.6,
        0.62,
        0.6,
        0.6,
        0.54,
        0.5,
    ]
    await r.async_update_adjusted_average(0.97)
    r.service.dtmodel.set_date(date(2023, 1, 30))
    await r.async_update_top_price(0.92)
    r.service.dtmodel.set_hour(11)
    await r.async_update_prices(prices)
    assert r.non_hours == []
