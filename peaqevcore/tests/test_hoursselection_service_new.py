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
async def test_last_nonhour_stopped_until_tomorrow_blank():
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 5, 20, 14, 0, 0))
    await service.async_update_prices(_p.P230520[0], _p.P230520[1])
    assert service.allowance.prefix_type == AllowanceType.AllowedUntil
    service.dtmodel.set_datetime(datetime(2023, 5, 20, 21, 0, 0))
    print(service.stopped_string)
    assert service.allowance.prefix_type == AllowanceType.AllowedUntilTomorrow
    service.dtmodel.set_datetime(datetime(2023, 5, 21, 1, 0, 0))
    await service.async_update_prices(_p.P230520[1], [])
    print(service.stopped_string)
    assert service.allowance.prefix_type == AllowanceType.AllowedUntil


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
    # print(service.offset_dict)


@pytest.mark.asyncio
async def test_offsets_230622():
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 6, 22, 15, 0, 0))
    await service.async_update_prices(_p.P230622[0], _p.P230622[1])
    assert service.offset_dict["today"][23] > service.offset_dict["tomorrow"][0]


@pytest.mark.asyncio
async def test_230620():
    opt = HourSelectionOptions(
        top_price=1.5, min_price=0.05, cautionhour_type_enum=CautionHourType.AGGRESSIVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 6, 20, 11, 27, 0))
    await service.async_update_prices(_p.P230620[0])
    assert sum([x.permittance for x in service.future_hours]) > 2.0


@pytest.mark.asyncio
async def test_230620_230621():
    h = Hoursselection(
        absolute_top_price=1.5,
        min_price=0.05,
        cautionhour_type=CautionHourType.AGGRESSIVE.value,
    )
    h.service.dtmodel.set_datetime(datetime(2023, 6, 20, 22, 12, 0))
    await h.service.async_update_prices(_p.P230620[0], _p.P230620[1])
    await h.service.max_min.async_setup(5)
    await h.service.max_min.async_update(0.4, 2.1, 5)
    print(await h.async_get_average_kwh_price())
    # assert 1 > 2


@pytest.mark.asyncio
async def test_total_charge():
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 6, 24, 20, 0, 0))
    await service.async_update_prices(_p.P230624[0], _p.P230624[1])
    for i in service.future_hours:
        print(i)
    assert 1 > 2
