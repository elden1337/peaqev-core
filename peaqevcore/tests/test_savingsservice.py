import pytest
import statistics as stat
from datetime import datetime
from ..services.savings.savings_service import SavingsService


@pytest.mark.asyncio
async def test_add_registered_consumption():
    s = SavingsService(0.5)
    _date = datetime(2021,3,24).date()
    _hour = 20
    for i in range(100):
        await s.model.async_add_to_registered_consumption(0.5, _date, _hour)
    assert s.model.registered_consumption[_date][_hour] == 50

@pytest.mark.asyncio
async def test_add_to_peak():
    s = SavingsService(0.5)
    _date = datetime(2021,3,24).date()
    _hour = 20
    for i in range(100):
        await s.model.async_add_to_peaks(0.5, _date, _hour)    
    assert s.model.peaks[_date][_hour] == 50
