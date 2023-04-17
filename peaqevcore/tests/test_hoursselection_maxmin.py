import pytest
import statistics as stat
from ..services.hourselection.hoursselection import Hoursselection as h
from ..models.hourselection.cautionhourtype import CautionHourType, VALUES_CONVERSION
from ..models.hourselection.topprice_type import TopPriceType

P230412 = [
    [0.54, 0.55, 0.57, 0.6, 0.62, 0.72, 0.74, 0.88, 0.9, 0.83, 0.77, 0.81, 0.77, 0.72, 0.61, 0.55, 0.51, 0.56, 0.58, 0.52, 0.44, 0.42, 0.34, 0.15],
    [0.07, 0.07, 0.06, 0.06, 0.06, 0.11, 0.41, 0.45, 0.47, 0.45, 0.44, 0.42, 0.4, 0.4, 0.35, 0.37, 0.39, 0.41, 0.41, 0.41, 0.39, 0.35, 0.29, 0.21]
]


@pytest.mark.asyncio
async def test_230412_maxmin_not_active():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE, absolute_top_price=30, min_price=0.0)
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    ret =await r.async_get_average_kwh_price()
    assert r.max_min.active is False
    assert r.max_min.average_price == ret[1]

@pytest.mark.asyncio
async def test_230412_maxmin_active_average_price():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE, absolute_top_price=30, min_price=0.0)
    peak= 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, 100)
    ret =await r.async_get_average_kwh_price()
    assert r.max_min.average_price == ret[1]

@pytest.mark.asyncio
async def test_230412_maxmin_active_average_price_decrease():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak= 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, max(1, initial_charge[0]-10))
    ret =await r.async_get_average_kwh_price()
    assert ret[1] is not None
    assert ret[1] <= ret[0]
    

@pytest.mark.asyncio
async def test_230412_maxmin_active_total_charge():
    r = h(cautionhour_type=CautionHourType.AGGRESSIVE, absolute_top_price=30, min_price=0.0)
    peak= 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, 100)
    ret =await r.async_get_total_charge(peak)
    assert r.max_min.total_charge == ret[1]
    assert ret[1] == ret[0]
    assert r.max_min.total_charge <= initial_charge[0]

@pytest.mark.asyncio
async def test_230412_maxmin_active_decrease_suave():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak= 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    print(initial_charge)
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, max(1, initial_charge[0]-10))
    ret =await r.async_get_total_charge(peak)
    assert r.max_min.total_charge == ret[1]
    assert ret[1] != ret[0]
    assert r.max_min.total_charge <= initial_charge[0]

@pytest.mark.asyncio
async def test_230412_maxmin_active_decrease_increase_suave():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak= 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    initial_charge = await r.async_get_total_charge(peak)
    await r.max_min.async_setup(100)
    assert r.max_min.active is True
    await r.max_min.async_update(0, peak, max(1, initial_charge[0]-10))
    ret =await r.async_get_total_charge(peak)
    assert r.max_min.total_charge == ret[1]
    assert ret[1] != ret[0]
    assert r.max_min.total_charge <= initial_charge[0]
    await r.max_min.async_update(0, peak, initial_charge[0]+10)
    ret =await r.async_get_total_charge(peak)
    assert r.max_min.total_charge == ret[1]
    assert ret[1] == ret[0]
    assert r.max_min.total_charge == initial_charge[0]

@pytest.mark.asyncio
async def test_230412_fixed_price():
    r = h(cautionhour_type=CautionHourType.SUAVE, absolute_top_price=30, min_price=0.0)
    peak= 2.28
    await r.async_update_adjusted_average(0.77)
    await r.service.async_set_day(12)
    await r.async_update_top_price(0.97)
    r.service._mock_hour = await r.service.async_set_hour(19)
    await r.async_update_prices(P230412[0], P230412[1])
    await r.max_min.async_setup(peak)
    await r.max_min.async_update(0, peak, peak/2)
    ret =await r.async_get_average_kwh_price()
    assert ret == (0.31, 0.06)
    





