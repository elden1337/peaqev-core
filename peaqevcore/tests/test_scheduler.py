from datetime import datetime
import pytest

from ..services.scheduler.scheduler import Scheduler
from ..models.hourselection.hourselection_options import HourSelectionOptions

MOCKPRICES = [
    0.422,
    0.341,
    0.309,
    0.322,
    0.331,
    0.422,
    0.773,
    1.169,
    1.794,
    1.975,
    2.119,
    1.849,
    1.309,
    1.24,
    1.137,
    1.122,
    1.14,
    1.3,
    1.397,
    1.971,
    1.377,
    1.178,
    1.05,
    0.709,
]
MOCKPRICES_TOMORROW = [
    0.513,
    0.452,
    0.458,
    0.413,
    0.377,
    0.498,
    0.693,
    2.145,
    2.193,
    2.191,
    2.184,
    2.168,
    2.153,
    2.144,
    2.135,
    2.12,
    2.134,
    2.156,
    2.165,
    2.159,
    2.146,
    2.121,
    2.081,
    0.983,
]


@pytest.mark.asyncio
async def test_scheduler_overnight_1():
    s = Scheduler(test=True)
    MOCKDT = datetime.strptime("22-07-20 19:00", "%y-%m-%d %H:%M")
    dep_time_obj = datetime.strptime("22-07-21 06:00", "%y-%m-%d %H:%M")
    await s.async_create(
        desired_charge=11, departuretime=dep_time_obj, starttime=MOCKDT
    )
    await s.async_update(
        avg24=710,
        peak=4.71,
        charged_amount=0,
        prices=MOCKPRICES,
        prices_tomorrow=MOCKPRICES_TOMORROW,
        mockdt=MOCKDT,
    )
    assert s.model.non_hours == [19, 20, 21, 22, 23, 0, 2, 5]
    assert s.model.hours_charge == {
        datetime(2022, 7, 21, 1, 0): 0.7,
        datetime(2022, 7, 21, 3, 0): 1,
        datetime(2022, 7, 21, 4, 0): 1,
    }


@pytest.mark.asyncio
async def test_scheduler_overnight_1_maxprice():
    opt = HourSelectionOptions(top_price=0.4)
    s = Scheduler(opt, test=True)
    MOCKDT = datetime.strptime("22-07-20 19:00", "%y-%m-%d %H:%M")
    dep_time_obj = datetime.strptime("22-07-21 06:00", "%y-%m-%d %H:%M")
    await s.async_create(
        desired_charge=11, departuretime=dep_time_obj, starttime=MOCKDT
    )
    await s.async_update(
        avg24=710,
        peak=4.71,
        charged_amount=0,
        prices=MOCKPRICES,
        prices_tomorrow=MOCKPRICES_TOMORROW,
        mockdt=MOCKDT,
    )
    assert s.model.non_hours == [19, 20, 21, 22, 23, 0, 1, 2, 3, 5]
    assert s.model.hours_charge == {datetime(2022, 7, 21, 4, 0): 1}


@pytest.mark.asyncio
async def test_scheduler_cancel_on_departure():
    s = Scheduler(test=True)
    MOCKDT = datetime.strptime("22-07-20 19:00", "%y-%m-%d %H:%M")
    dep_time_obj = datetime.strptime("22-07-21 06:00", "%y-%m-%d %H:%M")
    await s.async_create(
        desired_charge=11, departuretime=dep_time_obj, starttime=MOCKDT
    )
    await s.async_update(
        avg24=710,
        peak=4.71,
        charged_amount=0,
        prices=MOCKPRICES,
        prices_tomorrow=MOCKPRICES_TOMORROW,
        mockdt=MOCKDT,
    )
    await s.async_update(
        avg24=310,
        peak=4.71,
        charged_amount=0,
        prices=MOCKPRICES,
        prices_tomorrow=MOCKPRICES_TOMORROW,
        mockdt=dep_time_obj,
    )
    assert s.scheduler_active is False


@pytest.mark.asyncio
async def test_scheduler_overnight_2():
    s = Scheduler(test=True)
    MOCKDT = datetime.strptime("22-07-20 19:00", "%y-%m-%d %H:%M")
    midnight_dt = datetime.strptime("22-07-21 01:00", "%y-%m-%d %H:%M")
    dep_time_obj = datetime.strptime("22-07-21 06:00", "%y-%m-%d %H:%M")
    await s.async_create(
        desired_charge=11, departuretime=dep_time_obj, starttime=MOCKDT
    )
    await s.async_update(
        avg24=710,
        peak=4.71,
        charged_amount=0,
        prices=MOCKPRICES,
        prices_tomorrow=MOCKPRICES_TOMORROW,
        mockdt=MOCKDT,
    )
    assert s.model.non_hours == [19, 20, 21, 22, 23, 0, 2, 5]
    assert s.model.hours_charge == {
        datetime(2022, 7, 21, 1, 0): 0.7,
        datetime(2022, 7, 21, 3, 0): 1,
        datetime(2022, 7, 21, 4, 0): 1,
    }
    await s.async_update(
        avg24=710,
        peak=4.71,
        charged_amount=0,
        prices=MOCKPRICES_TOMORROW,
        mockdt=midnight_dt,
    )
    assert s.model.non_hours == [2, 5]


@pytest.mark.asyncio
async def test_scheduler_overnight_3():
    s = Scheduler(test=True)
    start_dt = datetime.strptime("22-07-20 11:00", "%y-%m-%d %H:%M")
    dep_time_dt = datetime.strptime("22-07-21 09:00", "%y-%m-%d %H:%M")
    await s.async_create(
        desired_charge=9, departuretime=dep_time_dt, starttime=start_dt
    )
    await s.async_update(
        avg24=410, peak=1.5, charged_amount=0, prices=MOCKPRICES, mockdt=start_dt
    )
    assert s.model.non_hours == [11, 18, 19, 20]
    await s.async_update(
        avg24=410,
        peak=1.5,
        charged_amount=1,
        prices=MOCKPRICES,
        mockdt=datetime.strptime("22-07-20 12:05", "%y-%m-%d %H:%M"),
    )
    await s.async_update(
        avg24=610,
        peak=1.5,
        charged_amount=0.7,
        prices=MOCKPRICES,
        prices_tomorrow=MOCKPRICES_TOMORROW,
        mockdt=datetime.strptime("22-07-20 13:01", "%y-%m-%d %H:%M"),
    )
    assert s.model.non_hours == [14, 15, 16, 17, 18, 19, 20, 21, 7, 8]
    await s.async_update(
        avg24=610,
        peak=1.5,
        charged_amount=0.7,
        prices=MOCKPRICES,
        prices_tomorrow=MOCKPRICES_TOMORROW,
        mockdt=datetime.strptime("22-07-20 22:11", "%y-%m-%d %H:%M"),
    )
    assert s.model.non_hours == [7, 8]
    await s.async_update(
        avg24=310,
        peak=1.5,
        charged_amount=1,
        prices=MOCKPRICES_TOMORROW,
        mockdt=datetime.strptime("22-07-21 00:03", "%y-%m-%d %H:%M"),
    )
    assert s.model.non_hours == [6, 7, 8]


@pytest.mark.asyncio
async def test_scheduler_overnight_no_charge():
    """this is fine. since there is no charge happening, the non-hours will be less and less as time to departure gets smaller"""
    s = Scheduler(test=True)
    start_dt = datetime.strptime("22-07-20 11:00", "%y-%m-%d %H:%M")
    dep_time_dt = datetime.strptime("22-07-21 09:00", "%y-%m-%d %H:%M")
    await s.async_create(
        desired_charge=9, departuretime=dep_time_dt, starttime=start_dt
    )
    await s.async_update(
        avg24=310, peak=1.5, charged_amount=0, prices=MOCKPRICES, mockdt=start_dt
    )
    assert s.model.non_hours == [11, 12, 18, 19, 20]
    await s.async_update(
        avg24=310,
        peak=1.5,
        charged_amount=0,
        prices=MOCKPRICES,
        mockdt=datetime.strptime("22-07-20 12:05", "%y-%m-%d %H:%M"),
    )
    await s.async_update(
        avg24=310,
        peak=1.5,
        charged_amount=0,
        prices=MOCKPRICES,
        prices_tomorrow=MOCKPRICES_TOMORROW,
        mockdt=datetime.strptime("22-07-20 13:01", "%y-%m-%d %H:%M"),
    )
    assert s.active == True
    assert s.model.non_hours == [14, 15, 16, 17, 18, 19, 20, 21, 22, 7, 8]
    await s.async_update(
        avg24=310,
        peak=1.5,
        charged_amount=0,
        prices=MOCKPRICES,
        prices_tomorrow=MOCKPRICES_TOMORROW,
        mockdt=datetime.strptime("22-07-20 22:11", "%y-%m-%d %H:%M"),
    )
    assert s.model.non_hours == [7, 8]
    await s.async_update(
        avg24=310,
        peak=1.5,
        charged_amount=0,
        prices=MOCKPRICES_TOMORROW,
        mockdt=datetime.strptime("22-07-21 00:03", "%y-%m-%d %H:%M"),
    )
    assert s.model.non_hours == [8]


@pytest.mark.asyncio
async def test_scheduler_start_after_departure():
    """this is fine. since there is no charge happening, the non-hours will be less and less as time to departure gets smaller"""
    s = Scheduler(test=True)
    start_dt = datetime.strptime("23-05-05 12:00", "%y-%m-%d %H:%M")
    dep_time_dt = datetime.strptime("23-05-05 07:00", "%y-%m-%d %H:%M")
    await s.async_create(
        desired_charge=9, departuretime=dep_time_dt, starttime=start_dt
    )
    assert s.active is False
