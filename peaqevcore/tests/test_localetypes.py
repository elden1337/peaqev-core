from datetime import datetime, date, time
import pytest
from ..models.locale.enums.querytype import QueryType
from ..services.locale.Locale import (
    LocaleFactory,
    LOCALE_SE_GOTHENBURG,
    LOCALE_BE_VREG,
    LOCALE_SE_BJERKE_ENERGI,
    LOCALE_SE_ELLEVIO,
    LOCALE_SE_JBF,
    LOCALE_SE_KRISTINEHAMN,
    LOCALE_SE_SKOVDE,
    LOCALE_SE_SOLLENTUNA,
    LOCALE_DEFAULT,
    LOCALE_NO_PEAK,
)
from ..services.locale.querytypes.const import (
    QUERYTYPE_AVERAGEOFTHREEDAYS,
    QUERYTYPE_AVERAGEOFTHREEHOURS,
    QUERYTYPE_SOLLENTUNA,
)
from ..services.locale.querytypes.querytypes import QUERYTYPES
from ..services.locale.countries.sweden import (
    SE_SHE_AB,
    SE_Bjerke_Energi,
    SE_Gothenburg,
    SE_Kristinehamn,
    SE_Skovde,
    SE_Sollentuna,
    SE_Ellevio,
    SE_JBF,
)
from ..services.locale.countries.default import NoPeak
from ..services.locale.locale_query import LocaleQuery, ILocaleQuery


@pytest.mark.asyncio
async def test_SE_Bjerke_Energi():
    p = await LocaleFactory.async_create(LOCALE_SE_BJERKE_ENERGI)

    assert await p.data.async_free_charge(mockdt=datetime(2005, 7, 14, 22, 30)) is True
    assert (
        await p.data.async_free_charge(
            mockdt=datetime.combine(date(2005, 7, 14), time(15, 00))
        )
        is False
    )
    del p


@pytest.mark.asyncio
async def test_generic_querytype_avg_threedays():
    pt = QUERYTYPES[QueryType.AverageOfThreeDays]
    await pt.async_reset()
    await pt.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 7, 14), time(20, 30))
    )
    await pt.async_try_update(
        new_val=2, timestamp=datetime.combine(date(2022, 7, 14), time(21, 30))
    )
    to_state_machine = pt.peaks.export_peaks
    await pt.peaks.async_set_init_dict(
        dict_data=to_state_machine, dt=datetime.combine(date(2022, 7, 14), time(23, 30))
    )
    await pt.async_try_update(
        new_val=0.6, timestamp=datetime.combine(date(2022, 7, 15), time(21, 30))
    )
    assert len(pt.peaks.p) == 2
    assert pt._charged_peak_value == 1.3
    del pt


@pytest.mark.asyncio
async def test_generic_querytype_avg_threedays2():
    pg = QUERYTYPES[QueryType.AverageOfThreeDays]
    await pg.async_reset()
    await pg.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 7, 14), time(20, 30))
    )
    await pg.async_try_update(
        new_val=2, timestamp=datetime.combine(date(2022, 7, 14), time(21, 30))
    )
    assert len(pg.peaks.p) == 1
    assert pg._charged_peak_value == 2
    del pg


@pytest.mark.asyncio
async def test_generic_querytype_avg_threedays3():
    to_state_machine = {"m": 7, "p": {"14h21": 2}}
    p1 = QUERYTYPES[QueryType.AverageOfThreeDays]
    await p1.async_reset()
    await p1.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 7, 15), time(21, 30))
    )
    await p1.peaks.async_set_init_dict(
        to_state_machine, datetime.combine(date(2022, 7, 15), time(21, 30))
    )
    assert len(p1.peaks.p) == 2
    assert p1.charged_peak == 1.5
    assert p1.observed_peak == 1
    await p1.async_try_update(
        new_val=2, timestamp=datetime.combine(date(2022, 7, 15), time(22, 30))
    )
    assert len(p1.peaks.p) == 2
    assert p1.charged_peak == 2
    assert p1.observed_peak == 2
    del p1


@pytest.mark.asyncio
async def test_faulty_number_in_import():
    to_state_machine = {
        "m": 7,
        "p": {"14h21": 2, "11h22": 1.49, "12h9": 1.93, "12h14": 0.73},
    }
    p1 = QUERYTYPES[QueryType.AverageOfThreeDays]
    await p1.async_reset()
    await p1.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 7, 15), time(21, 30))
    )
    await p1.peaks.async_set_init_dict(
        to_state_machine, datetime.combine(date(2022, 7, 15), time(21, 30))
    )
    assert len(p1.peaks.p) == 3
    assert p1.charged_peak == 1.81
    assert p1.observed_peak == 1.49
    await p1.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 15), time(22, 30))
    )
    assert len(p1.peaks.p) == 3
    assert p1.charged_peak == 1.81
    assert p1.observed_peak == 1.5
    del p1


@pytest.mark.asyncio
async def test_overridden_number_in_import():
    to_state_machine = {"m": 7, "p": {"11h22": 1.49, "12h9": 1.93, "13h16": 0.86}}
    p1 = QUERYTYPES[QueryType.AverageOfThreeDays]
    await p1.async_reset()
    await p1.async_try_update(
        new_val=0.22, timestamp=datetime.combine(date(2022, 7, 13), time(21, 30))
    )
    await p1.peaks.async_set_init_dict(
        to_state_machine, datetime.combine(date(2022, 7, 13), time(21, 30))
    )
    assert p1.charged_peak == 1.43
    del p1


@pytest.mark.asyncio
async def test_SE_Gothenburg():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    assert isinstance(p.data.query_model, LocaleQuery)
    assert await p.data.async_free_charge() is False
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 7, 14), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 7, 16), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 17), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.7, timestamp=datetime.combine(date(2022, 7, 17), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 19), time(22, 30))
    )
    assert p.data.query_model.observed_peak > 0
    del p


@pytest.mark.asyncio
async def test_generic_querytype_avg_threehour2s():
    p = await LocaleFactory.async_create(LOCALE_SE_SOLLENTUNA)
    assert isinstance(p.data.query_model, LocaleQuery)
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 7, 14), time(15, 30))
    )
    assert p.data.query_model.observed_peak == 1.2
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 7, 16), time(22, 30))
    )
    assert p.data.query_model.observed_peak == 1.2
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 18), time(11, 30))
    )
    assert p.data.query_model.observed_peak == 1.2
    assert p.data.query_model.charged_peak == 1.35
    await p.data.query_model.async_try_update(
        new_val=1.7, timestamp=datetime.combine(date(2022, 7, 18), time(17, 30))
    )
    assert p.data.query_model.observed_peak == 1.2
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 19), time(22, 30))
    )

    assert p.data.query_model.observed_peak == 1.2
    del p


@pytest.mark.asyncio
async def test_peak_new_month():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 6, 2), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 6, 16), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 6, 17), time(20, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.7, timestamp=datetime.combine(date(2022, 6, 17), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 6, 19), time(22, 30))
    )
    assert len(p.data.query_model.peaks.p) == 3
    assert p.data.query_model.observed_peak == 1.2
    await p.data.query_model.async_try_update(
        new_val=0.03, timestamp=datetime.combine(date(2022, 7, 1), time(0, 0))
    )
    assert len(p.data.query_model.peaks.p) == 1
    assert p.data.query_model.observed_peak == 0.03
    del p


@pytest.mark.asyncio
async def test_peak_new_hour():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 6, 1), time(1, 30))
    )
    assert p.data.query_model.peaks.p == {(1, 1): 1.2}
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 6, 1), time(6, 30))
    )
    assert p.data.query_model.peaks.p == {(1, 1): 1.2}
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 6, 1), time(9, 30))
    )
    assert p.data.query_model.peaks.p == {(1, 9): 1.5}
    del p


@pytest.mark.asyncio
async def test_peak_new_hour_multiple():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 7, 2), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 7, 16), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 17), time(20, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.7, timestamp=datetime.combine(date(2022, 7, 17), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 19), time(22, 30))
    )
    assert p.data.query_model.peaks.export_peaks == {
        "m": 7,
        "p": {"2h22": 1.2, "17h22": 1.7, "19h22": 1.5},
    }
    assert p.data.query_model.peaks.p == {(2, 22): 1.2, (17, 22): 1.7, (19, 22): 1.5}
    assert p.data.query_model.peaks.m == 7
    await p.data.query_model.async_try_update(
        new_val=2.5, timestamp=datetime.combine(date(2022, 7, 19), time(23, 30))
    )
    assert p.data.query_model.peaks.export_peaks == {
        "m": 7,
        "p": {"2h22": 1.2, "17h22": 1.7, "19h23": 2.5},
    }
    assert p.data.query_model.peaks.p == {(2, 22): 1.2, (17, 22): 1.7, (19, 23): 2.5}
    del p


@pytest.mark.asyncio
async def test_overridden_number_in_import_2():
    to_state_machine = {"m": 7, "p": {"1h15": 1.5}}
    p1 = QUERYTYPES[QueryType.AverageOfThreeDays]
    await p1.async_reset()
    await p1.async_try_update(
        new_val=0.22, timestamp=datetime.combine(date(2022, 7, 2), time(15, 30))
    )
    await p1.peaks.async_set_init_dict(
        to_state_machine, datetime.combine(date(2022, 7, 2), time(15, 30))
    )
    assert len(p1.peaks.p) == 2
    del p1


@pytest.mark.asyncio
async def test_is_quarterly():
    p2 = await LocaleFactory.async_create(LOCALE_BE_VREG)
    assert await p2.data.async_is_quarterly() is True
    del p2


@pytest.mark.asyncio
async def test_is_not_quarterly():
    p = await LocaleFactory.async_create(LOCALE_SE_KRISTINEHAMN)
    assert await p.data.async_is_quarterly() is False
    del p


@pytest.mark.asyncio
async def test_se_ellevio():
    p = await LocaleFactory.async_create(LOCALE_SE_ELLEVIO)
    assert await p.data.async_free_charge(mockdt=datetime.now()) is False
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 7, 14), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 7, 16), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 17), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.7, timestamp=datetime.combine(date(2022, 7, 17), time(22, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 19), time(22, 30))
    )
    assert p.data.query_model.observed_peak > 0
    del p


@pytest.mark.asyncio
async def test_se_jbf():
    p = await LocaleFactory.async_create(LOCALE_SE_JBF)
    assert (
        await p.data.async_free_charge(
            mockdt=datetime.combine(date(2023, 2, 14), time(21, 59))
        )
        is False
    )
    assert (
        await p.data.async_free_charge(
            mockdt=datetime.combine(date(2023, 2, 14), time(22, 1))
        )
        is True
    )
    assert (
        await p.data.async_free_charge(
            mockdt=datetime.combine(date(2023, 5, 17), time(12, 0))
        )
        is True
    )
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2023, 2, 6), time(10, 30))
    )
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2023, 2, 6), time(11, 30))
    )
    assert p.data.query_model.observed_peak == 1
    assert p.data.query_model.charged_peak == 1.1
    await p.data.query_model.async_try_update(
        new_val=2, timestamp=datetime.combine(date(2023, 2, 6), time(12, 30))
    )
    assert p.data.query_model.charged_peak == 1.4
    del p


# async def test_no_peak():
#     p = NoPeak
#     assert p.free_charge(p, mockdt=datetime.now()) is True
#     await p.query_model.async_try_update(new_val=1.5, timestamp=datetime.combine(date(2023, 7, 19), time(22, 30)))
#     assert p.query_model.charged_peak == 0


@pytest.mark.asyncio
async def test_peak_new_month_2():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 7, 2), time(22, 30))
    )
    print(p.data.query_model.peaks.p, p.data.query_model.observed_peak)
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 7, 16), time(22, 30))
    )
    print(p.data.query_model.peaks.p, p.data.query_model.observed_peak)
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 17), time(20, 30))
    )
    print(p.data.query_model.peaks.p, p.data.query_model.observed_peak)
    await p.data.query_model.async_try_update(
        new_val=1.7, timestamp=datetime.combine(date(2022, 7, 17), time(22, 30))
    )
    print(p.data.query_model.peaks.p, p.data.query_model.observed_peak)
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 19), time(22, 30))
    )
    print(p.data.query_model.peaks.p, p.data.query_model.observed_peak)
    assert len(p.data.query_model.peaks.p) == 3
    assert p.data.query_model.observed_peak == 1.2
    await p.data.query_model.async_try_update(
        new_val=0.03, timestamp=datetime.combine(date(2022, 8, 1), time(0, 0))
    )
    assert len(p.data.query_model.peaks.p) == 1
    assert p.data.query_model.observed_peak == 0.03
    del p

@pytest.mark.asyncio
async def test_avg_daily_same_peak_as_max_today():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime.combine(date(2024, 1, 3), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime.combine(date(2024, 1, 4), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=4.2, timestamp=datetime.combine(date(2024, 1, 5), time(10, 0)))
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 5), time(22, 0))) == 4.2
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 6), time(0, 0))) == 2


@pytest.mark.asyncio
async def test_avg_hourly_observed_peak():
    p = await LocaleFactory.async_create(LOCALE_SE_SOLLENTUNA)
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime.combine(date(2024, 1, 3), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime.combine(date(2024, 1, 4), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=4.2, timestamp=datetime.combine(date(2024, 1, 5), time(10, 0)))
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 5), time(22, 0))) == 2
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 6), time(0, 0))) == 2
