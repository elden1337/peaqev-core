from datetime import date, datetime, timedelta
import pytest
import statistics as stat

from ..services.hoursselection_service_new.models.permittance_type import PermittanceType
from ..services.hourselection.hoursselection import Hoursselection as h
from ..common.enums.cautionhourtype import CautionHourType
from ..models.hourselection.topprice_type import TopPriceType
from .prices import *

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
P240213 = [0.98,0.97,0.94,0.91,0.9,0.77,0.98,1.11,1.29,1.1,1.02,0.98,0.93,0.92,0.96,1.04,1.14,1.37,1.44,1.32,1.14,1.06,1.01,0.96]
P240214 = [0.71,0.72,0.71,0.7,0.69,0.71,0.94,1.07,1.17,1.03,0.98,0.97,0.96,0.96,1.02,1.06,1.15,1.21,1.27,1.23,1.12,0.84,0.76,0.72]
P240215 = [0.93,0.92,0.83,0.83,0.77,0.78,0.93,1.2,1.21,1.16,1.1,1.04,1,0.99,1.04,1.11,1.16,1.24,1.24,1.07,0.99,0.86,0.81,0.76]
P240824 = [-0.03, -0.07, -0.07, -0.07, -0.06, -0.03, -0.01, 0.03, 0.04, 0.04, 0.05, -0.01, -0.09, -0.07, -0.04, -0.06, 0.01, 0.06, 0.08, 0.08, 0.08, 0.08, 0.06, 0.05]
P240825 = [0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.06, 0.07, 0.07, 0.06, -0.01, -0.07, -0.14, -0.21, -0.21, -0.07, 0.01, 0.04, 0.06, 0.07, 0.07, 0.07, 0.07, 0.06]

P_ONLY_NEGATIVE = [-0.03, -0.07, -0.07, -0.07, -0.06, -0.03, -0.01, -0.03, -0.04, -0.04, -0.05, -0.01, -0.09, -0.07, -0.04, -0.06, -0.01, -0.06, -0.08, -0.08, -0.08, -0.08, -0.06, -0.05]


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
    #print(ret)
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
    await r.async_update_prices(prices=P230412[0], prices_tomorrow=P230412[1])
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
    await r.service.max_min.async_update(0, peak, 100)
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

from ..services.hoursselection_service_new.models.hour_type import HourType

@pytest.mark.asyncio
async def test_issue_325_wrong_hours():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=3, min_price=0.1)
    peak = 2.05
    await r.async_update_adjusted_average(1.02)
    await r.async_update_top_price(0.74)
    r.service.dtmodel.set_datetime(datetime(2024, 2, 13, 21, 0, 0))
    await r.async_update_prices(P240213, P240214)
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(1041, peak, 9)
    assert all(hour.hour_type is HourType.AboveMax for hour in r.future_hours if hour.price > 0.74)
    assert all(hour.permittance == 0 for hour in r.future_hours if hour.hour_type is HourType.AboveMax)
    
    assert [h.permittance for h in r.future_hours if h.dt == datetime(2024,2,14,0,0,0)][0] > 0
    assert [h.permittance for h in r.future_hours if h.dt == datetime(2024,2,14,1,0,0)][0] > 0
    assert [h.permittance for h in r.future_hours if h.dt == datetime(2024,2,14,2,0,0)][0] > 0
    assert [h.permittance for h in r.future_hours if h.dt == datetime(2024,2,14,3,0,0)][0] > 0

    assert(await r.async_get_total_charge(peak) == (15.1, 6.9))


@pytest.mark.asyncio
async def test_too_few_hours():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=3, min_price=0.1)
    peak = 2.05
    await r.async_update_adjusted_average(1.04)
    await r.async_update_top_price(0.93)
    r.service.dtmodel.set_datetime(datetime(2024, 2, 15, 13, 8, 0))
    await r.async_update_prices(P240215)
    assert(await r.async_get_total_charge(peak) == (10.2, None))

    before_hours = [hour.permittance for hour in r.future_hours]
    print(sum([hour.permittance for hour in r.future_hours]))
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(936, peak, 2)
    assert [hour.permittance for hour in r.future_hours] == before_hours
    print(sum([hour.permittance for hour in r.future_hours]))
    #assert(await r.async_get_total_charge(peak) == (10.2, 5.8))
    """deactivate maxmin"""
    await r.service.max_min.async_update(936, peak, 0)
    assert [hour.permittance for hour in r.future_hours] == before_hours
    print(sum([hour.permittance for hour in r.future_hours]))
    #assert 1 > 2

@pytest.mark.asyncio
async def test_cap_hours_keep_cap():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=3, min_price=0.1)
    peak = 2.05
    await r.async_update_adjusted_average(1.04)
    await r.async_update_top_price(0.93)
    r.service.dtmodel.set_datetime(datetime(2024, 2, 15, 13, 8, 0))
    await r.async_update_prices(P240215, P240214)
    assert all(hour.permittance_type is PermittanceType.Regular for hour in r.future_hours)
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(936, peak, 4, car_connected=True)
    assert max([hour.dt for hour in r.service.display_future_hours if hour.permittance_type is PermittanceType.MaxMin]) == datetime(2024,2,16,9,0,0)
    r.service.dtmodel.set_datetime(datetime(2024, 2, 16, 0, 8, 0))
    await r.service.max_min.async_update(930, peak, 4, car_connected=True)
    assert max([hour.dt for hour in r.service.display_future_hours if hour.permittance_type is PermittanceType.MaxMin]) == datetime(2024,2,16,9,0,0)


@pytest.mark.asyncio
async def test_230426_session_decrease_2():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.89)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 0, 0, 0))
    await r.async_update_prices(P230426[0])
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 13, 0, 0))
    await r.async_update_prices(P230426[0], P230426[1])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(0.7, 2.28, 5)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 18, 0, 0))
    await r.service.max_min.async_update(0.5, 2.28, 3.2)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 27, 0, 0, 0))
    await r.async_update_prices(P230426[1])
    

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
    #print(r.stopped_string)
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
    #print(r.non_hours)
    assert r.non_hours[1].hour == 17


@pytest.mark.asyncio
async def test_230426_session_map_correct_cheapest():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(10.89)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 13, 0, 0))
    await r.async_update_prices(P230426[0], P230426[1])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(700, peak, 5)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 16, 0, 0))
    _desired_decreased = 0.9
    await r.service.max_min.async_update(340, peak, _desired_decreased)
    assert r.service.max_min.total_charge == _desired_decreased


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
    await r.service.max_min.async_update(460, peak, 8)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 26, 16, 0, 0))
    available = [
        k.hour for k in r.service.max_min.model.input_hours if k.permittance > 0
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
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(0.46, peak, 2.2, car_connected=True)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 29, 16, 0, 0))
    available = [
        k.hour for k in r.service.max_min.model.input_hours if k.permittance > 0
    ]
    assert available[0] == 14
    _date += timedelta(days=1)
    _date = _date.replace(hour=14)
    r1 = next(filter(lambda x: _date == x.dt, r.service.max_min.model.input_hours))
    assert r1.permittance == 0.96
    await r.service.max_min.async_update(0.46, peak, 2.2, 0.2, True)
    r2 = next(filter(lambda x: _date == x.dt, r.service.max_min.model.input_hours))
    assert r2.permittance == 0.88
    await r.service.max_min.async_update(0.46, peak, 2.2, 0.4, True)
    r3 = next(filter(lambda x: _date == x.dt, r.service.max_min.model.input_hours))
    assert r3.permittance == 0.79
    await r.service.max_min.async_update(0.46, peak, 2.2, 1.4, True)
    r4 = next(filter(lambda x: _date == x.dt, r.service.max_min.model.input_hours))
    assert r4.permittance == 0.35


@pytest.mark.asyncio
async def test_230512_car_connected():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak = 1.68
    await r.async_update_adjusted_average(0.66)

    await r.async_update_top_price(0.86)

    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 14, 0, 0))
    await r.async_update_prices(P230512[0], P230512[1])
    await r.service.max_min.async_update(0.4, peak, 7)
    available = [
        k.hour for k in r.service.max_min.model.input_hours if k.permittance > 0
    ]
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 15, 0, 0))
    await r.service.max_min.async_update(0.4, peak, 7, car_connected=True)
    available2 = [
        k.hour for k in r.service.max_min.model.input_hours if k.permittance > 0
    ]
    assert available == available2
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 18, 0, 0))
    await r.service.max_min.async_update(0.4, peak, 7, car_connected=True)
    available3 = [
        k.hour for k in r.service.max_min.model.input_hours if k.permittance > 0
    ]
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
    await r.service.max_min.async_update(400, peak, 6)
    await r.service.max_min.async_update(400, peak, 4)
    await r.service.max_min.async_update(400, peak, 8)
    # print(r.non_hours)
    # assert 1 > 2
    # available = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    # r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 15, 0, 0))
    # await r.service.max_min.async_update(0.4, peak, 7, car_connected=True)
    # available2 = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    # assert available == available2
    # r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 18, 0, 0))
    # await r.service.max_min.async_update(0.4, peak, 7, car_connected=True)
    # available3 = [k for k, v in r.service.max_min.model.input_hours.items() if v[1] > 0]
    # assert available2 == available3


@pytest.mark.asyncio
async def test_230622_static_charge():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=1.5, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(avg24=0.4, peak=peak, max_desired=7)
    await r.service.max_min.async_update(avg24=0.4, peak=peak, max_desired=700)
    ret2 = await r.async_get_total_charge(peak)
    assert ret2[1] == ret2[0]


@pytest.mark.asyncio
async def test_230622_decrease_increase():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=1.5, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(avg24=400, peak=peak, max_desired=7)
    ret1 = await r.async_get_total_charge(peak)
    assert ret1[1] == 7
    await r.service.max_min.async_update(avg24=400, peak=peak, max_desired=12)
    ret2 = await r.async_get_total_charge(peak)
    assert ret2[1] == 12


@pytest.mark.asyncio
async def test_230622_decrease_increase_car_connected():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=1.5, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=7, car_connected=True
    )
    ret1 = await r.async_get_total_charge(peak)
    assert ret1[1] == 7
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=12, car_connected=True
    )
    ret2 = await r.async_get_total_charge(peak)
    assert ret2[1] == 12


@pytest.mark.asyncio
async def test_230622_decrease_increase_total_charge():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=1.5, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=7, car_connected=True
    )
    ret1 = await r.async_get_total_charge(peak)
    dyn1 = ret1[1] or 0
    stat1 = ret1[0]
    assert dyn1 <= ret1[0]
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=12, car_connected=True
    )
    ret2 = await r.async_get_total_charge(peak)
    assert ret2[0] == stat1
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=300, car_connected=True
    )
    ret3 = await r.async_get_total_charge(peak)
    assert ret3[1] == ret3[0]
    assert ret3[0] == stat1


@pytest.mark.asyncio
async def test_230622_decrease_increase_avgprice():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=1.5, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2020, 2, 12, 19, 0, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=7, car_connected=True
    )
    ret1 = await r.async_get_average_kwh_price()
    dyn1 = ret1[1] or 0.0
    stat1 = ret1[0] or 0.0
    assert dyn1 <= stat1
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=12, car_connected=True
    )
    ret2 = await r.async_get_average_kwh_price()
    assert ret2[0] == stat1
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=300, car_connected=True
    )
    ret3 = await r.async_get_average_kwh_price()
    assert ret3[1] == ret3[0]
    # when overridden with more than available, the dynamic price should be the same as the static.
    assert ret3[0] == stat1


@pytest.mark.asyncio
async def test_230622_update_prices():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=1.5, min_price=0.0)
    peak = 2.28
    await r.async_update_adjusted_average(0.77)
    await r.async_update_top_price(0.97)
    r.service.dtmodel.set_datetime(datetime(2023, 4, 12, 0, 0, 15))
    await r.async_update_prices(P230412[0])
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=5, car_connected=True
    )
    assert len(r.offsets["today"]) == 24
    assert r.offsets["tomorrow"] == {}
    r.service.dtmodel.set_datetime(datetime(2023, 4, 12, 13, 26, 15))
    await r.async_update_prices(P230412[0], P230412[1])
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=5, car_connected=True
    )
    future2 = r.future_hours
    offsets2 = r.offsets
    assert len(r.offsets["today"]) == 24
    assert len(r.offsets["tomorrow"]) == 24
    r.service.dtmodel.set_datetime(datetime(2023, 4, 13, 0, 0, 2))
    await r.async_update_prices(P230412[1])
    await r.async_update_adjusted_average(0.74)
    await r.service.max_min.async_update(
        avg24=400, peak=peak, max_desired=5, car_connected=True
    )
    assert r.future_hours == [f for f in future2 if f.dt.date() == date(2023, 4, 13)]
    assert r.offsets["today"] == offsets2["tomorrow"]
    assert r.offsets["tomorrow"] == {}

@pytest.mark.asyncio
async def test_resetting_maxmin_three_updates():
    peak = 1.76
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=1.5, min_price=0.0)
    await r.async_update_adjusted_average(0.43)
    r.service.dtmodel.set_datetime(datetime(2023, 8, 21, 0, 0, 4))
    await r.async_update_prices(P230821)
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(avg24=350, peak=peak, max_desired=9, car_connected=True)
    assert all([x.dt.day == 21 for x in r.future_hours])
    r.service.dtmodel.set_datetime(datetime(2023, 8, 21, 13, 40, 0))
    await r.async_update_prices(P230821, P230822)
    await r.service.max_min.async_update(avg24=350, peak=peak, max_desired=9, car_connected=True)
    print(len(r.service.all_hours))
    r.service.dtmodel.set_datetime(datetime(2023, 8, 22, 0, 1, 0))
    await r.async_update_prices(P230822, [])
    await r.service.max_min.async_update(avg24=350, peak=peak, max_desired=9, car_connected=True)
    assert all([x.dt.day == 22 for x in r.future_hours])
    print(sum([x.permittance for x in r.future_hours]))
    print(await r.async_get_total_charge(1.76))

@pytest.mark.asyncio
async def test_limiter_mostly_negative():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=3, min_price=0.1)
    peak = 1.9
    await r.async_update_adjusted_average(1.04)
    await r.async_update_top_price(0.15)
    r.service.dtmodel.set_datetime(datetime(2024, 8, 24, 19, 8, 0))
    await r.async_update_prices(P240824, P240825)
    assert all(hour.permittance_type is PermittanceType.Regular for hour in r.future_hours)
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(480, peak, 4, car_connected=True)
    hours_before_update = len([hour for hour in r.future_hours if hour.permittance > 0])
    assert hours_before_update > 0
    await r.service.max_min.async_update(480, peak, 4, car_connected=True, limiter=0.5)
    hours_after_update = len([hour for hour in r.future_hours if hour.permittance > 0])
    assert hours_after_update > hours_before_update

@pytest.mark.asyncio
async def test_limiter_only_negative():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=3, min_price=0.1)
    peak = 1.9
    await r.async_update_adjusted_average(1.04)
    await r.async_update_top_price(0.15)
    r.service.dtmodel.set_datetime(datetime(2024, 8, 24, 8, 8, 0))
    await r.async_update_prices(P_ONLY_NEGATIVE)
    assert all(hour.permittance_type is PermittanceType.Regular for hour in r.future_hours)
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(480, peak, 4, car_connected=True)
    hours_before_update = len([hour for hour in r.future_hours if hour.permittance > 0])
    assert hours_before_update > 0
    await r.service.max_min.async_update(480, peak, 4, car_connected=True, limiter=0.5)
    hours_after_update = len([hour for hour in r.future_hours if hour.permittance > 0])
    assert hours_after_update > hours_before_update

@pytest.mark.asyncio
async def test_limiter_no_negative():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=3, min_price=0.1)
    peak = 1.9
    await r.async_update_adjusted_average(1.04)
    await r.async_update_top_price(0.15)
    r.service.dtmodel.set_datetime(datetime(2023, 4, 12, 19, 8, 0))
    await r.async_update_prices(P230412[0], P230412[1])
    assert all(hour.permittance_type is PermittanceType.Regular for hour in r.future_hours)
    await r.service.max_min.async_setup(peak)
    await r.service.max_min.async_update(480, peak, 4, car_connected=True)
    hours_before_update = len([hour for hour in r.future_hours if hour.permittance > 0])
    assert hours_before_update > 0
    await r.service.max_min.async_update(480, peak, 4, car_connected=True, limiter=0.5)
    hours_after_update = len([hour for hour in r.future_hours if hour.permittance > 0])
    assert hours_after_update > hours_before_update

