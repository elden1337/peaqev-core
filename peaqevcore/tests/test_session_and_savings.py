from ..services.session.session_service import SessionService
from ..services.savings.savings_service import SavingsService
import pytest
from datetime import datetime


PRICES1 = [
    0.61,
    0.58,
    0.57,
    0.57,
    0.62,
    0.65,
    0.85,
    1.02,
    1.05,
    1.04,
    1.03,
    0.89,
    0.84,
    0.78,
    0.73,
    0.73,
    0.76,
    0.89,
    0.92,
    0.9,
    0.85,
    0.72,
    0.63,
    0.51,
]


@pytest.mark.asyncio
async def test_wait_charge_same_day_onephase_with_session():
    s = SavingsService(peak_price=36.25)
    _original_peak = 2.5
    _prices = PRICES1
    _connect_car_at = datetime(2023, 4, 20, 12, 00, 0)
    await s.async_add_prices(_date=_connect_car_at.date(), prices=_prices)
    await s.async_start_listen(_connect_car_at)
    _date = _connect_car_at.date()
    _hour = _connect_car_at.hour
    _cons = 0.1
    for i in range(660):
        await s.async_add_to_consumption(0.5, _date, _hour)
        if i % 60 == 0:
            _hour += 1
            _cons += 0.1
    # _mock_charge_draw = {_connect_car_at.date(): {21: 1.2, 22: 1.2, 23: 1.6}}
    session = SessionService()
    timer = datetime(2023, 4, 20, 21, 0, 0).timestamp()
    await session.async_setup(mock_time=timer)
    await session.async_update_price(6, timer)
    await session.async_update_power_reading(1200, timer)
    timer += 3600
    await session.async_update_price(3, timer)
    await session.async_update_power_reading(1200, timer)
    timer += 3600
    await session.async_update_power_reading(1600, timer)
    await session.async_terminate(timer)
    print(session.session_data)
    await s.async_register_charge_session(session.session_data, _original_peak)
    assert s.savings_peak == 14.5
    assert s.savings_trade == 0.79
    await s.async_stop_listen()
