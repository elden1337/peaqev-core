from datetime import datetime, timedelta
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

P230429 = [
    [
        1.35,
        1.35,
        1.28,
        1.28,
        1.27,
        1.25,
        1.26,
        1.31,
        1.32,
        1.33,
        1.27,
        1.14,
        0.97,
        0.73,
        0.66,
        0.63,
        0.66,
        0.66,
        0.73,
        0.7,
        0.68,
        0.64,
        0.46,
        0.42,
    ],
    [
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
    ],
]

P230512 = [
    [
        0.27,
        0.28,
        0.34,
        0.43,
        0.43,
        0.46,
        0.68,
        1.27,
        1.43,
        1.26,
        1.24,
        0.99,
        0.82,
        0.7,
        0.61,
        0.6,
        0.61,
        0.77,
        0.88,
        0.89,
        0.78,
        0.76,
        0.7,
        0.63,
    ],
    [
        0.44,
        0.43,
        0.43,
        0.44,
        0.45,
        0.45,
        0.4,
        0.4,
        0.42,
        0.42,
        0.4,
        0.35,
        0.3,
        0.16,
        0.15,
        0.17,
        0.35,
        0.42,
        0.43,
        0.43,
        0.42,
        0.42,
        0.36,
        0.25,
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
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    ret = await r.async_get_average_kwh_price()
    assert r.service.max_min.active is False
    assert r.service.max_min.average_price == ret[1]


@pytest.mark.asyncio
async def test_230412_maxmin_active_average_price():
    r = h(
        cautionhour_type=CautionHourType.AGGRESSIVE,
        absolute_top_price=30,
        min_price=0.0,
    )
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    await r.service.max_min.async_setup(100)
    assert r.service.max_min.active is True
    await r.service.max_min.async_update(0, peak, 100)
    ret = await r.async_get_average_kwh_price()
    assert r.service.max_min.average_price == ret[1]


@pytest.mark.asyncio
async def test_230412_maxmin_active_average_price_decrease():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.service.max_min.async_setup(100)
    assert r.service.max_min.active is True
    await r.service.max_min.async_update(0, peak, max(1, initial_charge[0] - 10))
    ret = await r.async_get_average_kwh_price()
    assert ret[1] is not None
    print(ret)
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
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.service.max_min.async_setup(100)
    assert r.service.max_min.active is True
    await r.service.max_min.async_update(0, peak, 100)
    ret = await r.async_get_total_charge(peak)
    assert r.service.max_min.total_charge == ret[1]
    assert ret[1] == ret[0]
    assert r.service.max_min.total_charge <= initial_charge[0]


@pytest.mark.asyncio
async def test_230412_maxmin_active_decrease_suave():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.service.max_min.async_setup(100)
    assert r.service.max_min.active is True
    await r.service.max_min.async_update(0, peak, max(1, initial_charge[0] - 40))
    ret = await r.async_get_total_charge(peak)
    assert r.service.max_min.total_charge == ret[1]
    assert ret[1] != ret[0]
    assert r.service.max_min.total_charge <= initial_charge[0]


@pytest.mark.asyncio
async def test_230412_maxmin_original_charge_static():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.service.max_min.async_setup(100)
    assert r.service.max_min.active is True
    initial_charge2 = await r.async_get_total_charge(peak)
    assert initial_charge2[0] == initial_charge[0]
    await r.service.max_min.async_update(0, peak, max(1, initial_charge[0] - 40))
    initial_charge3 = await r.async_get_total_charge(peak)
    assert initial_charge3[0] == initial_charge[0]


@pytest.mark.asyncio
async def test_230412_maxmin_active_decrease_increase_suave():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.service.max_min.async_setup(100)
    assert r.service.max_min.active is True
    await r.service.max_min.async_update(0, peak, max(1, initial_charge[0] - 10))
    ret = await r.async_get_total_charge(peak)
    assert r.service.max_min.total_charge == ret[1]
    assert ret[1] != ret[0]
    assert r.service.max_min.total_charge <= initial_charge[0]
    await r.service.max_min.async_update(0, peak, initial_charge[0] + 10)
    ret = await r.async_get_total_charge(peak)
    assert r.service.max_min.total_charge == ret[1]
    assert ret[1] == ret[0]
    assert r.service.max_min.total_charge == initial_charge[0]


@pytest.mark.asyncio
async def test_230412_fixed_price():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(0, peak, peak / 2)
    ret = await r.async_get_average_kwh_price()
    assert ret == (0.31, 0.06)


@pytest.mark.asyncio
async def test_230426_session_decrease():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.89)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 14, 0, 0))
    await r.async_update_prices(P230426[0], P230426[1])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(0.7, 2.28, 5)
    n = [n.hour for n in r.non_hours]
    assert n == [
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
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 18, 0, 0))
    await r.service.max_min.async_update(0.5, 2.28, 3.2)
    n2 = [n.hour for n in r.non_hours]
    assert n2 == [
        18,
        19,
        20,
        21,
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
        19,
        20,
        21,
        22,
        23,
    ]
    print(r.service.stopped_string)
    assert r.service.max_min.total_charge == 3.2


@pytest.mark.asyncio
async def test_230426_session_new_prices():
    r = h(
        cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=30, min_price=0.0
    )
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.89)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 13, 0, 0))
    await r.async_update_prices(P230426[0], P230426[1])
    await r.service.max_min.async_update(0.7, peak, 5)
    assert r.non_hours[1].hour == 17


@pytest.mark.asyncio
async def test_230426_session_map_correct_cheapest():
    r = h(
        cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=30, min_price=0.0
    )
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(10.89)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 13, 0, 0))
    await r.async_update_prices(P230426[0], P230426[1])
    await r.service.max_min.async_update(0.7, peak, 5)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 16, 0, 0))
    _desired_decreased = 2.4
    await r.service.max_min.async_update(3.4, peak, _desired_decreased)
    # print(r.non_hours)
    # print(r.dynamic_caution_hours)
    # print(r.service.max_min.total_charge)
    available_charge = round(
        sum([v[1] for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0])
        * peak,
        1,
    )
    assert r.service.max_min.total_charge == available_charge == _desired_decreased


@pytest.mark.asyncio
async def test_230429_session_map_correct_cheapest():
    r = h(
        cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=30, min_price=0.0
    )
    peak = 2.28
    await r.async_update_adjusted_average(1)
    await r.async_update_top_price(0.93)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 29, 15, 0, 0))
    await r.async_update_prices(P230429[0], P230429[1])
    await r.service.max_min.async_update(0.46, peak, 8)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 16, 0, 0))
    available = [
        k.hour for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0
    ]
    assert available == [11, 12, 13, 14]


@pytest.mark.asyncio
async def test_230429_session_map_single_hour():
    r = h(
        cautionhour_type=CautionHourType.SCROOGE, absolute_top_price=30, min_price=0.0
    )
    peak = 2.28
    await r.async_update_adjusted_average(1)
    await r.async_update_top_price(0.93)
    _date = datetime(2020, 2, 29, 15, 0, 0)
    r.service.dtmodel.set_datetime(_date)
    await r.async_update_prices(P230429[0], P230429[1])
    await r.service.max_min.async_update(0.46, peak, 2.2)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 29, 16, 0, 0))
    available = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    assert available[0].hour == 14
    _date += timedelta(days=1)
    _date = _date.replace(hour=14)
    assert r.service.max_min.model.input_hours[_date][1] == 1
    await r.service.max_min.async_update(0.46, peak, 2.2, 0.2)
    assert r.service.max_min.model.input_hours[_date][1] == 1
    await r.service.max_min.async_update(0.46, peak, 2.2, 0.4)
    assert r.service.max_min.model.input_hours[_date][1] == 1
    await r.service.max_min.async_update(0.46, peak, 2.2, 1.4)
    assert r.service.max_min.model.input_hours[_date][1] == 1


@pytest.mark.asyncio
async def test_230512_car_connected():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 1.68
    await r.async_update_adjusted_average(0.66)

    await r.async_update_top_price(0.86)

    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 14, 0, 0))
    await r.async_update_prices(P230512[0], P230512[1])
    await r.service.max_min.async_update(0.4, peak, 7)
    available = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 15, 0, 0))
    await r.service.max_min.async_update(0.4, peak, 7, car_connected=True)
    available2 = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    assert available == available2
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 18, 0, 0))
    await r.service.max_min.async_update(0.4, peak, 7, car_connected=True)
    available3 = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    assert available2 == available3


@pytest.mark.asyncio
async def test_230620_non_hours():
    r = h(
        cautionhour_type=CautionHourType.AGGRESSIVE,
        absolute_top_price=1.5,
        min_price=0.0,
    )
    peak = 2.1
    p = [
        0.9,
        0.9,
        0.89,
        0.89,
        0.89,
        0.9,
        0.94,
        1.07,
        1.23,
        1.09,
        1.03,
        0.99,
        1.01,
        0.95,
        0.94,
        0.95,
        0.98,
        1.02,
        1.08,
        1.11,
        1,
        0.96,
        0.92,
        0.9,
    ]
    await r.async_update_adjusted_average(0.66)
    await r.async_update_top_price(0.86)
    r.service.dtmodel.set_datetime(datetime(2023, 6, 20, 11, 3, 32))
    await r.async_update_prices(p)
    await r.service.max_min.async_update(0.4, peak, 7)
    print(r.non_hours)
    assert 1 > 2
    # available = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    # r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 15, 0, 0))
    # await r.service.max_min.async_update(0.4, peak, 7, car_connected=True)
    # available2 = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    # assert available == available2
    # r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 18, 0, 0))
    # await r.service.max_min.async_update(0.4, peak, 7, car_connected=True)
    # available3 = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    # assert available2 == available3
