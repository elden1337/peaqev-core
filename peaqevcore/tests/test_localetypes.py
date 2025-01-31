import asyncio
from datetime import datetime, date, time, timedelta
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
    LOCALE_NO_LINJA, LOCALE_SE_TEST,
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
from ..models.hub.currentpeak import CurrentPeak


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
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 6, 2), time(22, 30)))
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 6, 2), time(22, 30))
    )
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 6, 16), time(22, 30)))
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 6, 16), time(22, 30))
    )
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 6, 17), time(20, 30)))
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 6, 17), time(20, 30))
    )
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 6, 17), time(22, 30)))
    await p.data.query_model.async_try_update(
        new_val=1.7, timestamp=datetime.combine(date(2022, 6, 17), time(22, 30))
    )
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 6, 19), time(22, 30)))
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 6, 19), time(22, 30))
    )
    assert len(p.data.query_model.peaks.p) == 3
    assert p.data.query_model.observed_peak == 1.5
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 6, 20), time(22, 30)))
    assert p.data.query_model.observed_peak == 1.2
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 7, 1), time(0, 0)))
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

@pytest.mark.asyncio
async def test_peak_new_month_2():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 7, 2), time(22, 30)))
    await p.data.query_model.async_try_update(
        new_val=1.2, timestamp=datetime.combine(date(2022, 7, 2), time(22, 30))
    )

    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 7, 16), time(22, 30)))
    await p.data.query_model.async_try_update(
        new_val=1, timestamp=datetime.combine(date(2022, 7, 16), time(22, 30))
    )
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 7, 17), time(20, 30)))
    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 17), time(20, 30))
    )
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 7, 17), time(22, 30)))
    await p.data.query_model.async_try_update(
        new_val=1.7, timestamp=datetime.combine(date(2022, 7, 17), time(22, 30))
    )
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 7, 19), time(22, 30)))

    await p.data.query_model.async_try_update(
        new_val=1.5, timestamp=datetime.combine(date(2022, 7, 19), time(22, 30))
    )
    assert len(p.data.query_model.peaks.p) == 3
    assert p.data.query_model.observed_peak == 1.5
    p.data.query_model.set_mock_dt(datetime.combine(date(2022, 8, 1), time(0, 0)))
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
async def test_average_of_three_days_should_increase_daily_peak():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    c = CurrentPeak(data_type=float, initval=0, startpeaks={}, locale=p, options_use_history=False, mock_dt=datetime(2024, 1, 3, 10, 0))
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime(2024, 1, 3, 10, 0))
    c.observed_peak = 2
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime(2024, 1, 4, 10, 0))
    c.mock_dt = datetime(2024, 1, 4, 10, 0)
    c.observed_peak = 2
    await p.data.query_model.async_try_update(new_val=4.2, timestamp=datetime(2024, 1, 5, 10, 0))
    c.mock_dt = datetime(2024, 1, 5, 10, 0)
    p.data.query_model.set_mock_dt(datetime(2024, 1, 5, 10, 0))
    c.observed_peak = 4.2
    assert c.observed_peak == 4.2
    c.dt = datetime(2024, 1, 6, 0, 0)
    p.data.query_model.set_mock_dt(datetime(2024, 1, 6, 0, 0))
    assert c.observed_peak == 2

@pytest.mark.asyncio
async def test_average_of_three_hours_should_not_increase_daily_peak():
    p = await LocaleFactory.async_create(LOCALE_SE_SOLLENTUNA)
    c = CurrentPeak(data_type=float, initval=0, startpeaks={}, locale=p, options_use_history=False, mock_dt=datetime(2024, 1, 3, 10, 0))
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime(2024, 1, 3, 10, 0))
    c.observed_peak = 2
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime(2024, 1, 4, 10, 0))
    c.mock_dt = datetime(2024, 1, 4, 10, 0)
    c.observed_peak = 2
    await p.data.query_model.async_try_update(new_val=4.2, timestamp=datetime(2024, 1, 5, 10, 0))
    c.mock_dt = datetime(2024, 1, 5, 10, 0)
    p.data.query_model.set_mock_dt(datetime(2024, 1, 5, 10, 0))
    c.observed_peak = 4.2
    assert c.observed_peak == 2

@pytest.mark.asyncio
async def test_avg_daily_real_case_should_show_min():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    c = CurrentPeak(data_type=float, initval=0, startpeaks={}, locale=p, options_use_history=False, mock_dt=datetime(2024, 4, 1, 0, 0))
    await p.data.query_model.async_try_update(new_val=2.76, timestamp=datetime(2024, 4, 3, 1, 0))
    c.dt = datetime(2024, 4, 3, 1, 0)
    c.observed_peak = 2.76
    await p.data.query_model.async_try_update(new_val=2.79, timestamp=datetime(2024, 4, 7, 8, 0))
    c.dt = datetime(2024, 4, 7, 8, 0)
    c.observed_peak = 2.79
    await p.data.query_model.async_try_update(new_val=2.47, timestamp=datetime(2024, 4, 14, 16, 0))
    c.dt = datetime(2024, 4, 14, 16, 0)
    c.observed_peak = 2.47
    c.dt = datetime(2024, 4, 16, 21, 0)
    p.data.query_model.set_mock_dt(datetime(2024, 4, 16, 21, 0))
    assert c.observed_peak == 2.47
    assert c.history == {'2024_4': [2.76, 2.79, 2.47]}

@pytest.mark.asyncio
async def test_avg_daily_real_case_should_show_min_with_history_import():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    c = CurrentPeak(data_type=float, initval=0, startpeaks={}, locale=p, options_use_history=False, mock_dt=datetime(2024, 4, 16, 0, 0))
    c.import_from_service(importdto={'2024_4': [2.76, 2.79, 2.47]})
    c.dt = datetime(2024, 4, 16, 21, 0)
    p.data.query_model.set_mock_dt(datetime(2024, 4, 16, 21, 0))
    assert c.observed_peak == 2.47
    assert c.history == {'2024_4': [2.76, 2.79, 2.47]}


@pytest.mark.asyncio
async def test_avg_hourly_observed_peak():
    p = await LocaleFactory.async_create(LOCALE_SE_SOLLENTUNA)
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime.combine(date(2024, 1, 3), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime.combine(date(2024, 1, 4), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=4.2, timestamp=datetime.combine(date(2024, 1, 5), time(10, 0)))
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 5), time(22, 0))) == 2
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 6), time(0, 0))) == 2


@pytest.mark.asyncio
async def test_tiered_pricing():
    p = await LocaleFactory.async_create(LOCALE_NO_LINJA)
    await p.data.query_model.async_try_update(new_val=2.05, timestamp=datetime.combine(date(2024, 1, 3), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=2.7, timestamp=datetime.combine(date(2024, 1, 4), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=2.81, timestamp=datetime.combine(date(2024, 1, 5), time(10, 0)))
    #p.data.price.get_observed_peak
    cc = p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 6), time(0, 0)))
    print(cc)
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 6), time(0, 0))) == 4.9


@pytest.mark.asyncio
async def test_register_correct_new_peak2():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    await p.data.query_model.async_try_update(new_val=3, timestamp=datetime.combine(date(2024, 1, 3), time(10, 0)))
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 3), time(10, 1))) == 3
    assert len(p.data.query_model.peaks.p) == 1

    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime.combine(date(2024, 1, 4), time(10, 0)))
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 4), time(10, 1))) == 2
    assert len(p.data.query_model.peaks.p) == 2

    await p.data.query_model.async_try_update(new_val=4, timestamp=datetime.combine(date(2024, 1, 5), time(10, 0)))
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 5), time(10, 1))) == 4
    assert len(p.data.query_model.peaks.p) == 3

    await p.data.query_model.async_try_update(new_val=4, timestamp=datetime.combine(date(2024, 1, 6), time(10, 0)))
    assert (4,10) not in p.data.query_model.peaks.p.keys()

    await p.data.query_model.async_try_update(new_val=4.01, timestamp=datetime.combine(date(2024, 1, 6), time(11, 0)))
    assert (6, 11) in p.data.query_model.peaks.p.keys()
    assert p.data.query_model.peaks.p[(6,11)] == 4.01

@pytest.mark.asyncio
async def test_register_correct_swap_hours():
    p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
    await p.data.query_model.async_try_update(new_val=3, timestamp=datetime.combine(date(2024, 1, 3), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime.combine(date(2024, 1, 4), time(10, 0)))
    await p.data.query_model.async_try_update(new_val=4, timestamp=datetime.combine(date(2024, 1, 5), time(10, 0)))
    assert p.data.query_model.get_currently_obeserved_peak(datetime.combine(date(2024, 1, 5), time(10, 1))) == 4
    assert len(p.data.query_model.peaks.p) == 3

    assert p.data.query_model.peaks.p[(5,10)] == 4
    await p.data.query_model.async_try_update(new_val=0, timestamp=datetime.combine(date(2024, 1, 5), time(10, 59, 59)))
    assert p.data.query_model.peaks.p[(5,10)] == 4 #should still be the same since we tried to push a lower value for the same hour.


#-----------test se
@pytest.mark.asyncio
async def test_test_se_should_free_charge_christmas_eve():
    p = await LocaleFactory.async_create(LOCALE_SE_TEST)
    test_dt = datetime(2024, 12,24, 10, 30)
    check = await p.data.async_free_charge(mockdt=test_dt)
    assert check is True

@pytest.mark.asyncio
async def test_test_se_should_free_charge_winter_weekends():
    p = await LocaleFactory.async_create(LOCALE_SE_TEST)
    test_dt = datetime(2024, 12,22, 10, 30)
    check = await p.data.async_free_charge(mockdt=test_dt)
    assert check is True

@pytest.mark.asyncio
async def test_test_se_should_free_charge_winter_weeknights():
    p = await LocaleFactory.async_create(LOCALE_SE_TEST)
    test_dt = datetime(2024, 12,23, 10, 30)
    check = await p.data.async_free_charge(mockdt=test_dt)
    assert check is False
    test_dt = datetime(2024, 12, 23, 22, 30)
    check = await p.data.async_free_charge(mockdt=test_dt)
    assert check is True

@pytest.mark.asyncio
async def test_test_se_should_free_charge_all_summer():
    p = await LocaleFactory.async_create(LOCALE_SE_TEST)
    test_dt = datetime(2024, 6,23, 10, 30)
    for i in range(0,7):
        check = await p.data.async_free_charge(mockdt=test_dt)
        assert check is True
        test_dt += timedelta(days=1)
