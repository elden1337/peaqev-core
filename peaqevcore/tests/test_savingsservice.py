import pytest
import statistics as stat
from datetime import datetime, timedelta
from ..services.savings.savings_service import SavingsService

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
PRICES2 = [
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


@pytest.mark.asyncio
async def test_add_consumption():
    s = SavingsService(peak_price=36.25)
    assert not s.model.consumption
    _date = datetime(2021, 3, 24).date()
    _hour = 20
    await s.async_start_listen()
    for i in range(100):
        await s.async_add_to_consumption(0.5 + (i / 10), _date, _hour)
    assert s.model.consumption[_date][_hour] == 10.4


@pytest.mark.asyncio
async def test_add_consumption_not_collecting():
    s = SavingsService(peak_price=36.25)
    _date = datetime(2021, 3, 24).date()
    _hour = 20
    for i in range(100):
        await s.async_add_to_consumption(0.5, _date, _hour)
    assert _date not in s.model.consumption.keys()


@pytest.mark.asyncio
async def test_calculate_estimated_power_and_energy():
    s = SavingsService(peak_price=36.25)
    _connect_car_at = datetime(2023, 4, 20, 12, 00, 0)
    _mock_charge_draw = {_connect_car_at.date(): {21: 1.2, 22: 1.2, 23: 1.6}}
    _ = await s.async_calculate_estimated_power(_mock_charge_draw)
    assert _[0] == 1333
    assert _[1] == 4


@pytest.mark.asyncio
async def test_calculate_charge_cost():
    s = SavingsService(peak_price=36.25)
    _connect_car_at = datetime(2023, 4, 20, 12, 00, 0)
    await s.async_add_prices(_date=_connect_car_at.date(), prices=PRICES1)
    _mock_charge_draw = {_connect_car_at.date(): {21: 1.2, 22: 1.2, 23: 1.6}}
    _assumed_sum = sum(
        [v * PRICES1[k] for k, v in _mock_charge_draw[_connect_car_at.date()].items()]
    )
    assert await s.async_calculate_charge_cost(_mock_charge_draw) == _assumed_sum


@pytest.mark.asyncio
async def test_wait_charge_same_day_onephase():
    s = SavingsService(peak_price=36.25)
    _original_peak = 2.5
    _prices = PRICES1
    _connect_car_at = datetime(2023, 4, 20, 12, 00, 0)
    await s.async_add_prices(_date=_connect_car_at.date(), prices=_prices)
    await s.async_start_listen(_connect_car_at)
    _date = _connect_car_at.date()
    _hour = _connect_car_at.hour
    # register the draw before charging begins
    _cons = 0.1
    for i in range(660):
        await s.async_add_to_consumption(0.5, _date, _hour)
        # await s.async_add_to_peaks(0.5, _date, _hour)
        if i % 60 == 0:
            _hour += 1
            _cons += 0.1
    # this should come from session-service later, but i need to add per hour there as well.
    _mock_charge_draw = {_connect_car_at.date(): {21: 1.2, 22: 1.2, 23: 1.6}}
    await s.async_register_charge_session(_mock_charge_draw, _original_peak)
    assert s.savings_peak == 0
    assert s.savings_trade == 0.7
    # finalize
    await s.async_stop_listen()


@pytest.mark.asyncio
async def test_wait_charge_same_day_threephase():
    s = SavingsService(peak_price=36.25)
    _original_peak = 2.5
    _prices = PRICES1
    _connect_car_at = datetime(2023, 4, 20, 12, 00, 0)
    await s.async_add_prices(_date=_connect_car_at.date(), prices=_prices)
    await s.async_start_listen(_connect_car_at)
    _date = _connect_car_at.date()
    _hour = _connect_car_at.hour
    # register the draw before charging begins
    _cons = 0.1
    for i in range(660):
        await s.async_add_to_consumption(0.5 + (_cons), _date, _hour)
        # await s.async_add_to_peaks(0.5, _date, _hour)
        if i % 60 == 0:
            _hour += 1
            _cons += 0.1
    # this should come from session-service later, but i need to add per hour there as well.
    _mock_charge_draw = {_connect_car_at.date(): {21: 5.2, 22: 5.2, 23: 4.6}}
    await s.async_register_charge_session(_mock_charge_draw, _original_peak)
    assert s.savings_peak == 155.88
    assert s.savings_trade == 2.38
    # finalize
    await s.async_stop_listen()


@pytest.mark.asyncio
async def test_wait_charge_next_day_threephase():
    s = SavingsService(peak_price=36.25)
    _original_peak = 2.5
    _prices = PRICES1
    _prices_tomorrow = PRICES2
    _connect_car_at = datetime(2023, 4, 20, 12, 43, 0)
    _date = _connect_car_at.date()
    _hour = _connect_car_at.hour
    await s.async_add_prices(_date=_date, prices=_prices)
    await s.async_add_prices(_date=(_date + timedelta(days=1)), prices=_prices_tomorrow)
    await s.async_start_listen(_connect_car_at)
    # register the draw before charging begins
    _cons = 0.1
    _min = _connect_car_at.minute
    for i in range(1200):
        await s.async_add_to_consumption(0.5 + (_cons), _date, _hour)
        # await s.async_add_to_peaks(0.5, _date, _hour)
        _min += 1
        if _min == 60:
            _min = 0
            _hour += 1
            if _hour == 24:
                _hour = 0
                _date = (_connect_car_at + timedelta(days=1)).date()
            _cons += 0.1
        print(_date, _hour, _min)
    # this should come from session-service later, but i need to add per hour there as well.
    _mock_charge_draw = {
        _connect_car_at.date(): {23: 3},
        (_connect_car_at + timedelta(days=1)).date(): {2: 5.2, 3: 5.2, 4: 5, 5: 3},
    }
    await s.async_register_charge_session(_mock_charge_draw, _original_peak)
    assert s.savings_peak == 174
    assert s.savings_trade == 14.89
    # finalize
    await s.async_stop_listen()


# listen to if a certain hour is free-charge in the locale-model
