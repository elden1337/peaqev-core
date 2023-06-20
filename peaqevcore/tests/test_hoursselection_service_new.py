import pytest
from ..services.hourselection.hoursselection import Hoursselection
from peaqevcore.services.hoursselection_service_new.models.stop_string import (
    AllowanceType,
)
from ..services.hoursselection_service_new.hourselection_service import (
    HourSelectionService,
)
from ..models.hourselection.hourselection_options import HourSelectionOptions
from ..models.hourselection.cautionhourtype import CautionHourType, VALUES_CONVERSION
from ..models.hourselection.topprice_type import TopPriceType
import peaqevcore.tests.prices as _p
from datetime import date, timedelta, datetime


@pytest.mark.asyncio
async def test_passed_hours_auto_update():
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2021, 1, 1, 21, 0, 0))
    await service.async_update_prices(_p.P230520[0], _p.P230520[1])
    assert len([x for x in service.all_hours if x.passed]) == 21
    service.dtmodel.set_datetime(datetime(2021, 1, 2, 6, 0, 0))
    assert len([x for x in service.all_hours if x.passed]) == 30


@pytest.mark.asyncio
async def test_passed_hours_empty_seq():
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2021, 1, 1, 21, 0, 0))
    await service.async_update_prices(_p.P230520[0], _p.P230520[1])
    assert len(service.future_hours) > 0
    service.dtmodel.set_datetime(datetime(2021, 1, 3, 0, 0, 0))
    assert len(service.future_hours) == 0


@pytest.mark.asyncio
async def test_last_nonhour_stopped_until():
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2021, 1, 1, 14, 0, 0))
    await service.async_update_prices(_p.P230520[0], _p.P230520[1])
    assert service.allowance.prefix_type == AllowanceType.AllowedUntil
    service.dtmodel.set_datetime(datetime(2021, 1, 2, 18, 0, 0))
    assert service.allowance.prefix_type == AllowanceType.StoppedUntil


@pytest.mark.asyncio
async def test_offsets_today_only():
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2021, 1, 1, 9, 0, 0))
    await service.async_update_prices(_p.P230520[0])
    print(service.offset_dict)
    assert len(service.offset_dict["today"]) == 24


@pytest.mark.asyncio
async def test_offsets_230613():
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2021, 1, 1, 14, 0, 0))
    await service.async_update_prices(_p.P230613[0], _p.P230613[1])
    print(service.offset_dict)


@pytest.mark.asyncio
async def test_230620():
    opt = HourSelectionOptions(
        top_price=1.5, min_price=0.05, cautionhour_type_enum=CautionHourType.AGGRESSIVE
    )
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
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 6, 20, 11, 27, 0))
    await service.async_update_prices(p)
    assert sum([x.permittance for x in service.future_hours]) > 2.0


@pytest.mark.asyncio
async def test_230620_230621():
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
    p2 = [
        0.9,
        0.83,
        0.78,
        0.79,
        0.86,
        0.91,
        0.94,
        1.06,
        1.21,
        1.1,
        1.01,
        0.95,
        0.95,
        0.94,
        0.93,
        0.94,
        0.94,
        0.95,
        0.95,
        0.94,
        0.91,
        0.9,
        0.83,
        0.74,
    ]
    h = Hoursselection(
        absolute_top_price=1.5,
        min_price=0.05,
        cautionhour_type=CautionHourType.AGGRESSIVE.value,
    )
    h.service.dtmodel.set_datetime(datetime(2023, 6, 20, 22, 12, 0))
    await h.service.async_update_prices(p, p2)
    await h.service.max_min.async_setup(5)
    await h.service.max_min.async_update(0.4, 2.1, 5)
    print(await h.async_get_average_kwh_price())
    assert 1 > 2
