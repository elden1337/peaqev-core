from datetime import datetime, date, time
import pytest
from ..models.locale.enums.querytype import QueryType
from ..services.locale.Locale import (
    LocaleFactory,
    LOCALE_SE_TEKNISKA_VERKEN_TARIFF_2
)
from ..services.locale.querytypes.const import (
    QUERYTYPE_AVERAGEOFTHREEDAYS,
    QUERYTYPE_AVERAGEOFTHREEHOURS,
    QUERYTYPE_SOLLENTUNA,
)
from ..services.locale.querytypes.querytypes import QUERYTYPES
from ..services.locale.countries.sweden import (SE_TekniskaVerken_TARIFF_2)

from ..services.locale.locale_query import LocaleQuery, ILocaleQuery
from ..models.hub.currentpeak import CurrentPeak

@pytest.mark.asyncio
async def test_1():
    #23-05 is "low"
    #06-22 is "high"
    p = await LocaleFactory.async_create(LOCALE_SE_TEKNISKA_VERKEN_TARIFF_2)
    
    p.data.query_model.set_mock_dt(datetime(2024, 1, 5, 10, 0))
    await p.data.query_model.async_try_update(new_val=2, timestamp=datetime(2024, 1, 5, 10, 0))
    assert p.data.query_model.observed_peak == 2

    p.data.query_model.set_mock_dt(datetime(2024, 1, 5, 23, 0))
    await p.data.query_model.async_try_update(new_val=3, timestamp=datetime(2024, 1, 5, 23, 0))
    assert p.data.query_model.observed_peak == 3

    p.data.query_model.set_mock_dt(datetime(2024, 1, 6, 7, 0))
    assert p.data.query_model.observed_peak == 2
    

@pytest.mark.asyncio
async def test_import_multipeaks_correct_keys():
    #23-05 is "low"
    #06-22 is "high"
    to_state_machine = {
        "high": {"1h15": 1.5}, 
        "low": {"2h22": 1.2}
        }
    p = await LocaleFactory.async_create(LOCALE_SE_TEKNISKA_VERKEN_TARIFF_2)
    
    p.data.query_model.set_mock_dt(datetime(2024, 1, 5, 10, 0))
    await p.data.query_model.async_import_from_service(to_state_machine)
    assert p.data.query_model.observed_peak == 1.5
    p.data.query_model.set_mock_dt(datetime(2024, 1, 6, 2, 0))
    assert p.data.query_model.observed_peak == 1.2


@pytest.mark.asyncio
async def test_import_multipeaks_incorrect_keys_too_many():
    #23-05 is "low"
    #06-22 is "high"
    to_state_machine = {
        "high": {"1h15": 1.5}, 
        "low": {"2h22": 1.2},
        "medium": {"2h22": 1.2}
        }
    p = await LocaleFactory.async_create(LOCALE_SE_TEKNISKA_VERKEN_TARIFF_2)
    p.data.query_model.set_mock_dt(datetime(2024, 1, 5, 10, 0))
    with pytest.raises(Exception):
        await p.data.query_model.async_import_from_service(to_state_machine)
    

@pytest.mark.asyncio
async def test_import_multipeaks_incorrect_keys_wrong_names():
    #23-05 is "low"
    #06-22 is "high"
    to_state_machine = {
        "high": {"1h15": 1.5}, 
        "summer": {"2h22": 1.2},
        }
    p = await LocaleFactory.async_create(LOCALE_SE_TEKNISKA_VERKEN_TARIFF_2)
    p.data.query_model.set_mock_dt(datetime(2024, 1, 5, 10, 0))
    with pytest.raises(Exception):
        await p.data.query_model.async_import_from_service(to_state_machine)
    


# @pytest.mark.asyncio
# async def test_2():
#     #23-05 is "low"
#     #06-22 is "high"
#     p = await LocaleFactory.async_create(LOCALE_SE_TEKNISKA_VERKEN_TARIFF_2)
    
#     p.data.query_model.set_mock_dt(datetime(2024, 1, 5, 10, 0))
#     await p.data.query_model.async_try_update(new_val=2, timestamp=datetime(2024, 1, 5, 10, 0))
#     assert p.data.query_model.observed_peak == 2

#     p.data.query_model.set_mock_dt(datetime(2024, 1, 5, 23, 0))
#     await p.data.query_model.async_try_update(new_val=3, timestamp=datetime(2024, 1, 5, 23, 0))
#     assert p.data.query_model.observed_peak == 3

#     p.data.query_model.set_mock_dt(datetime(2024, 1, 6, 7, 0))
#     assert p.data.query_model.observed_peak == 2

# @pytest.mark.asyncio
# async def test_peak_new_hour_multiple():
#     p = await LocaleFactory.async_create(LOCALE_SE_GOTHENBURG)
#     await p.data.query_model.async_try_update(
#         new_val=1.2, timestamp=datetime.combine(date(2022, 7, 2), time(22, 30))
#     )
#     await p.data.query_model.async_try_update(
#         new_val=1, timestamp=datetime.combine(date(2022, 7, 16), time(22, 30))
#     )
#     await p.data.query_model.async_try_update(
#         new_val=1.5, timestamp=datetime.combine(date(2022, 7, 17), time(20, 30))
#     )
#     await p.data.query_model.async_try_update(
#         new_val=1.7, timestamp=datetime.combine(date(2022, 7, 17), time(22, 30))
#     )
#     await p.data.query_model.async_try_update(
#         new_val=1.5, timestamp=datetime.combine(date(2022, 7, 19), time(22, 30))
#     )
#     assert p.data.query_model.peaks.export_peaks == {
#         "m": 7,
#         "p": {"2h22": 1.2, "17h22": 1.7, "19h22": 1.5},
#     }
#     assert p.data.query_model.peaks.p == {(2, 22): 1.2, (17, 22): 1.7, (19, 22): 1.5}
#     assert p.data.query_model.peaks.m == 7
#     await p.data.query_model.async_try_update(
#         new_val=2.5, timestamp=datetime.combine(date(2022, 7, 19), time(23, 30))
#     )
#     assert p.data.query_model.peaks.export_peaks == {
#         "m": 7,
#         "p": {"2h22": 1.2, "17h22": 1.7, "19h23": 2.5},
#     }
#     assert p.data.query_model.peaks.p == {(2, 22): 1.2, (17, 22): 1.7, (19, 23): 2.5}
#     del p


