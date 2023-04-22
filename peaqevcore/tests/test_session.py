from ..services.session.session_service import SessionService

import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_session_fluctuate():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_price(0.6, timer)
    await s.async_update_power_reading(6000, timer)
    timer += 1200
    await s.async_update_price(0.3, timer)
    await s.async_update_power_reading(3000, timer)
    timer += 1200
    await s.async_terminate(timer)
    assert s.total_energy == 3
    assert round(s.total_price, 4) == 1.5


@pytest.mark.asyncio
async def test_session_fluctuate_tenfold():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_price(6, timer)
    await s.async_update_power_reading(6000, timer)
    timer += 1200
    await s.async_update_price(3, timer)
    await s.async_update_power_reading(3000, timer)
    timer += 1200
    await s.async_terminate(timer)
    assert s.total_energy == 3
    assert round(s.total_price, 4) == 15


@pytest.mark.asyncio
async def test_session_split_price():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_price(2, timer)
    await s.async_update_power_reading(2000, timer)
    timer += 900
    await s.async_update_price(3, timer)
    timer += 900
    await s.async_update_power_reading(1000, timer)
    timer += 1800
    await s.async_terminate(timer)

    assert s.total_energy == 1.5
    assert s.total_price == 4


@pytest.mark.asyncio
async def test_session_full_hour():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_price(1, timer)
    await s.async_update_power_reading(1000, timer)
    timer += 3600
    await s.async_update_power_reading(1000, timer)
    await s.async_terminate(timer)
    assert s.total_energy == 1
    assert s.total_price == 1


@pytest.mark.asyncio
async def test_session_full_hour_no_price():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_power_reading(1000, timer)
    timer += 3600
    await s.async_update_power_reading(1000, timer)
    # await s.async_terminate(timer)
    assert s.total_energy == 1


@pytest.mark.asyncio
async def test_session_half_hour():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_price(1, timer)
    await s.async_update_power_reading(1000, timer)
    timer += 1800
    await s.async_update_power_reading(1000, timer)
    await s.async_terminate(timer)
    assert s.total_energy == 0.5
    assert s.total_price == 0.5


@pytest.mark.asyncio
async def test_session_with_zero_periods():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_price(2, timer)
    await s.async_update_power_reading(4000, timer)
    timer += 900
    # 2kr
    await s.async_update_power_reading(0, timer)
    timer += 900
    # 2kr
    await s.async_update_price(3, timer)
    timer += 900
    # 2kr
    await s.async_update_power_reading(1000, timer)
    timer += 1800
    # 3.5kr
    await s.async_terminate(timer)

    assert s.total_energy == 1.5
    assert s.total_price == 3.5


@pytest.mark.asyncio
async def test_session_with_zero_periods_price_update_in_between():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_price(2, timer)
    await s.async_update_power_reading(4000, timer)
    timer += 900
    # 2kr
    await s.async_update_price(3, timer)
    timer += 900
    # 5kr
    await s.async_update_power_reading(0, timer)
    timer += 900
    # 5kr
    await s.async_update_power_reading(1000, timer)
    timer += 1800
    # 6.5kr
    await s.async_terminate(timer)

    assert s.total_energy == 2.5
    assert s.total_price == 6.5


@pytest.mark.asyncio
async def test_session_get_status():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_price(2, timer)
    await s.async_update_power_reading(4000, timer)
    timer += 900
    status = await s.async_get_status()
    assert status["price"] == 0
    await s.async_update_price(3, timer)
    timer += 900
    status = await s.async_get_status()
    assert status["price"] == 2
    await s.async_update_power_reading(0, timer)
    timer += 900
    status = await s.async_get_status()
    assert status["price"] == 5
    # 5kr
    await s.async_update_power_reading(1000, timer)
    timer += 1800
    status = await s.async_get_status()
    assert status["price"] == 5
    assert status["energy"]["value"] == 2
    await s.async_terminate(timer)

    assert s.total_energy == 2.5
    assert s.total_price == 6.5


@pytest.mark.asyncio
async def test_session_get_statistics():
    s = SessionService()
    timer = 1651607299
    await s.async_setup(mock_time=timer)
    await s.async_update_price(2, timer)
    await s.async_update_power_reading(4000, timer)
    timer += 900
    status = await s.async_get_status()
    await s.async_update_price(3, timer)
    timer += 900
    status = await s.async_get_status()
    await s.async_update_power_reading(0, timer)
    timer += 900
    status = await s.async_get_status()
    await s.async_update_power_reading(1000, timer)
    timer += 1800
    status = await s.async_get_status()
    assert status["energy"]["value"] == 2
    await s.async_terminate(timer)
    assert s.total_energy == 2.5
    assert s.average_data.average == 2.5
    export = s.average_data.export
    assert export[datetime.fromtimestamp(timer).weekday()]["total_charge"] == 2.5
