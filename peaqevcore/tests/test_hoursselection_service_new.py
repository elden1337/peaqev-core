import pytest

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
