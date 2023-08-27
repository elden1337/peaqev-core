import pytest
from ..services.hourselection.hoursselection import Hoursselection
from peaqevcore.services.hoursselection_service_new.models.stop_string import (
    AllowanceType,
)
from ..services.hoursselection_service_new.hourselection_service import (
    HourSelectionService,
)
from ..models.hourselection.hourselection_options import HourSelectionOptions
from ..common.enums.cautionhourtype import CautionHourType
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
    assert service.allowance.prefix_type == AllowanceType.StoppedUntil
    service.dtmodel.set_datetime(datetime(2023, 5, 21, 1, 0, 0))
    await service.async_update_prices(_p.P230520[1], [])
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
    service.dtmodel.set_datetime(datetime(2023, 6, 24, 21, 0, 0))
    await service.async_update_prices(_p.P230624[0], _p.P230624[1])
    assert [h.hour for h in service.future_hours if h.permittance > 0] == [
        10,
        11,
        12,
        13,
        14,
        15,
        16
    ]


@pytest.mark.asyncio
async def test_total_charge_maxmin():
    # should be three hours, two full and one almost full.
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    peak = 2.2
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 6, 24, 14, 0, 0))
    await service.async_update_prices(_p.P230624[0], _p.P230624[1])
    await service.max_min.async_setup(peak)
    await service.max_min.async_update(520, peak, 5, car_connected=True)
    assert [h.hour for h in service.display_future_hours if h.permittance > 0] == [14, 11,12]
    assert service.max_min.total_charge == 5


@pytest.mark.asyncio
async def test_now_hour_in_nonhours():
    opt = HourSelectionOptions(
        top_price=2, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    peak = 2.2
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 6, 25, 14, 0, 0))
    await service.async_update_prices(_p.P230625[0], _p.P230625[1])
    await service.max_min.async_setup(peak)
    await service.max_min.async_update(520, peak, 5, car_connected=True)
    service.dtmodel.set_datetime(datetime(2023, 6, 25, 20, 47, 35))
    _ = [hp.dt for hp in service.future_hours if hp.permittance == 0.0]
    assert service.dtmodel.dt.replace(minute=0, second=0, microsecond=0) in _
    assert service.max_min.average_price == 0.27
    assert service.max_min.total_charge == 5


@pytest.mark.asyncio
async def test_assure_future_charge():
    opt = HourSelectionOptions(
        top_price=3, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    peak = 2.2
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 6, 25, 14, 0, 0))
    await service.async_update_prices(_p.P230625[0], _p.P230625[1])
    service.dtmodel.set_datetime(datetime(2023, 6, 25, 20, 47, 35))
    assert sum([hp.permittance * peak for hp in service.future_hours]) == 2.2
    service.dtmodel.set_datetime(datetime(2023, 6, 26, 0, 0, 10))
    await service.async_update_prices(_p.P230625[1])
    assert sum([hp.permittance * peak for hp in service.future_hours]) == 2.2
    #assert 1 > 2


@pytest.mark.asyncio
async def test_offsets_update_midnight():
    opt = HourSelectionOptions(
        top_price=3, min_price=0.05, cautionhour_type_enum=CautionHourType.SUAVE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 6, 25, 14, 0, 0))
    await service.async_update_prices(_p.P230625[0], _p.P230625[1])
    service.dtmodel.set_datetime(datetime(2023, 6, 25, 20, 47, 35))
    assert len(service.offset_dict["today"]) == 24
    offsets_tomorrow = service.offset_dict["tomorrow"]
    assert len(offsets_tomorrow) == 24
    service.dtmodel.set_datetime(datetime(2023, 6, 26, 0, 0, 10))
    await service.async_update_prices(_p.P230625[1])
    print(service.offset_dict)
    assert len(service.offset_dict["today"]) == 24
    assert len(service.offset_dict["tomorrow"]) == 0
    assert service.offset_dict["today"] == offsets_tomorrow

@pytest.mark.asyncio
async def test_shallow_curve():
    opt = HourSelectionOptions(
        top_price=1.5, min_price=0.05, cautionhour_type_enum=CautionHourType.INTERMEDIATE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 7, 13, 20, 30, 0))
    await service.async_update_prices(_p.P230713[0], _p.P230713[1])
    await service.async_update_adjusted_average(0.87)
    assert [h.hour for h in service.future_hours if h.permittance == 0] == [20,21,9,19]
    

@pytest.mark.asyncio
async def test_230721():
    opt = HourSelectionOptions(
        top_price=1.5, min_price=0.05, cautionhour_type_enum=CautionHourType.INTERMEDIATE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 7, 21, 19, 56, 0))
    await service.async_update_prices(_p.P230721[0], _p.P230721[1])
    await service.async_update_adjusted_average(0.47)
    assert [h.hour for h in service.future_hours if h.permittance > 0] == [0,1,2,3,4,5,6,7,11,12,13,14,15,16,23]


@pytest.mark.asyncio
async def test_offsets():
    opt = HourSelectionOptions(
        top_price=1.5, min_price=0.05, cautionhour_type_enum=CautionHourType.INTERMEDIATE
    )
    service = HourSelectionService(opt)
    service.dtmodel.set_datetime(datetime(2023, 7, 21, 0, 0, 2))
    await service.async_update_prices(_p.P230721[0])
    assert len(service.offset_dict["today"]) == 24
    assert len(service.offset_dict["tomorrow"]) == 0
    service.dtmodel.set_datetime(datetime(2023, 7, 21, 13, 56, 0))
    await service.async_update_prices(_p.P230721[0], _p.P230721[1])
    assert len(service.offset_dict["today"]) == 24
    assert len(service.offset_dict["tomorrow"]) == 24
    service.dtmodel.set_datetime(datetime(2023, 7, 22, 0, 1, 0))
    await service.async_update_prices(_p.P230721[1])
    await service.async_update_adjusted_average(0.47)
    assert len(service.offset_dict["today"]) == 24
    assert len(service.offset_dict["tomorrow"]) == 0