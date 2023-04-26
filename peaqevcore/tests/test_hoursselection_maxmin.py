import pytest
import statistics as stat
from ..services.hourselection.hoursselection import Hoursselection as h
from ..models.hourselection.cautionhourtype import CautionHourType, VALUES_CONVERSION
from ..models.hourselection.topprice_type import TopPriceType

P230412 = [
    [
        0.54,
        0.55,
        0.57,
        0.6,
        0.62,
        0.72,
        0.74,
        0.88,
        0.9,
        0.83,
        0.77,
        0.81,
        0.77,
        0.72,
        0.61,
        0.55,
        0.51,
        0.56,
        0.58,
        0.52,
        0.44,
        0.42,
        0.34,
        0.15,
    ],
    [
        0.07,
        0.07,
        0.06,
        0.06,
        0.06,
        0.11,
        0.41,
        0.45,
        0.47,
        0.45,
        0.44,
        0.42,
        0.4,
        0.4,
        0.35,
        0.37,
        0.39,
        0.41,
        0.41,
        0.41,
        0.39,
        0.35,
        0.29,
        0.21,
    ],
]
P230426 = [
    [
        0.62,
        0.61,
        0.61,
        0.6,
        0.6,
        0.68,
        0.91,
        1.16,
        1.22,
        1.14,
        1.13,
        0.89,
        0.8,
        0.68,
        0.64,
        0.58,
        0.65,
        1.01,
        1.06,
        1.11,
        1.13,
        1.13,
        1.01,
        0.69,
    ],
    [
        1.42,
        1.35,
        1.29,
        1.28,
        1.28,
        1.48,
        1.72,
        2.09,
        1.94,
        1.55,
        1.43,
        1.39,
        1.34,
        1.33,
        1.34,
        1.32,
        1.32,
        1.45,
        1.61,
        1.78,
        2.26,
        1.75,
        1.6,
        1.46,
    ],
]


@pytest.mark.asyncio
async def test_230412_maxmin_not_active():
    r = h(
        cautionhour_type=CautionHourType.AGGRESSIVE,
        absolute_top_price=30,
        min_price=0.0,
    )
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    ret = await r.async_get_average_kwh_price()
    assert r.max_min.active is False
    assert r.max_min.average_price == ret[1]


@pytest.mark.asyncio
async def test_230412_maxmin_active_average_price():
    r = h(
        cautionhour_type=CautionHourType.AGGRESSIVE,
        absolute_top_price=30,
        min_price=0.0,
    )
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, 100)
    ret = await r.async_get_average_kwh_price()
    assert r.max_min.average_price == ret[1]


@pytest.mark.asyncio
async def test_230412_maxmin_active_average_price_decrease():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, max(1, initial_charge[0] - 10))
    ret = await r.async_get_average_kwh_price()
    assert ret[1] is not None
    assert ret[1] <= ret[0]


@pytest.mark.asyncio
async def test_230412_maxmin_active_total_charge():
    r = h(
        cautionhour_type=CautionHourType.AGGRESSIVE,
        absolute_top_price=30,
        min_price=0.0,
    )
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, 100)
    ret = await r.async_get_total_charge(peak)
    assert r.max_min.total_charge == ret[1]
    assert ret[1] == ret[0]
    assert r.max_min.total_charge <= initial_charge[0]


@pytest.mark.asyncio
async def test_230412_maxmin_active_decrease_suave():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    print(initial_charge)
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, max(1, initial_charge[0] - 10))
    ret = await r.async_get_total_charge(peak)
    assert r.max_min.total_charge == ret[1]
    assert ret[1] != ret[0]
    assert r.max_min.total_charge <= initial_charge[0]


@pytest.mark.asyncio
async def test_230412_maxmin_active_decrease_increase_suave():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, max(1, initial_charge[0] - 10))
    ret = await r.async_get_total_charge(peak)
    assert r.max_min.total_charge == ret[1]
    assert ret[1] != ret[0]
    assert r.max_min.total_charge <= initial_charge[0]
    await r.max_min.async_update(0, peak, initial_charge[0] + 10)
    ret = await r.async_get_total_charge(peak)
    assert r.max_min.total_charge == ret[1]
    assert ret[1] == ret[0]
    assert r.max_min.total_charge == initial_charge[0]


@pytest.mark.asyncio
async def test_230412_fixed_price():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    await r.max_min.async_setup(peak)
    await r.max_min.async_update(0, peak, peak / 2)
    ret = await r.async_get_average_kwh_price()
    assert ret == (0.31, 0.06)


@pytest.mark.asyncio
async def test_230426_session_decrease():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(26)
    await r.async_update_top_price(0.89)
    r.service._mock_hour = await r.service.async_set_hour(14)
    await r.async_update_prices(P230426[0], P230426[1])
    await r.max_min.async_setup(peak)
    await r.max_min.async_update(0.7, 2.28, 5)
    assert r.non_hours == [
        17,
        18,
        19,
        20,
        21,
        22,
        23,
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
    ]
    r.service._mock_hour = await r.service.async_set_hour(18)
    await r.max_min.async_update(0.5, 2.28, 3.2)
    # original_all = {k: v for k, v in r.max_min.model.original_input_hours.items()}
    # print(f"original-all: {original_all}")
    # tweak_non = {k: v for k, v in r.max_min.model.input_hours.items() if v[1] == 0}
    # print(f"tweaked-no: {tweak_non}")
    # print(f"16: {P230426[0][16]}, {P230426[1][16]}")
    # print(f"17: {P230426[0][17]}, {P230426[1][17]}")
    # tweak = {k: v for k, v in r.max_min.model.input_hours.items() if v[1] > 0}
    # print(f"tweaked-yes: {tweak}")
    assert r.non_hours == [
        18,
        19,
        20,
        21,
        22,
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
    ]
    assert r.max_min.total_charge == 2.3


@pytest.mark.asyncio
async def test_230426_session_new_prices():
    r = h(
        cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=30, min_price=0.0
    )
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(26)
    await r.async_update_top_price(0.89)
    r.service._mock_hour = await r.service.async_set_hour(13)
    await r.async_update_prices(P230426[0], P230426[1])
    await r.max_min.async_update(0.7, peak, 5)
    assert r.non_hours[1] == 17
