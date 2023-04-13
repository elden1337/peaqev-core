# import pytest
# from ..services.hourselection.hourselectionservice.max_min_charge import MaxMinCharge

# class Helpers:
#     @staticmethod
#     async def setup_init_today_tomorrow():        
#         non_hours = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 21]
#         prices = [0.54, 0.55, 0.57, 0.6, 0.62, 0.72, 0.74, 0.88, 0.9, 0.83, 0.77, 0.81, 0.77, 0.72, 0.61, 0.55, 0.51, 0.56, 0.58, 0.52, 0.44, 0.42, 0.34, 0.15]
#         prices_tomorrow = [0.07, 0.07, 0.06, 0.06, 0.06, 0.11, 0.41, 0.45, 0.47, 0.45, 0.44, 0.42, 0.4, 0.4, 0.35, 0.37, 0.39, 0.41, 0.41, 0.41, 0.39, 0.35, 0.29, 0.21]
#         dynamic_caution_hours = {}
#         h = MaxMinCharge()
#         await h.async_setup(non_hours, dynamic_caution_hours, prices, prices_tomorrow, mock_hour = 21)
#         return h    
    
#     @staticmethod
#     async def setup_init_today(mock_hour:int|None=None):        
#         non_hours = [5,6,7,8,9, 10, 11, 12, 13]
#         prices = [0.54, 0.55, 0.57, 0.6, 0.62, 0.72, 0.74, 0.88, 0.9, 0.83, 0.77, 0.81, 0.77, 0.72, 0.61, 0.55, 0.51, 0.56, 0.58, 0.52, 0.44, 0.42, 0.34, 0.15]
#         prices_tomorrow = []
#         dynamic_caution_hours = {}
#         h = MaxMinCharge()
#         await h.async_make_hours(non_hours, dynamic_caution_hours, prices, prices_tomorrow, mock_hour = mock_hour)
#         return h    

# @pytest.fixture
# def helpers():
#     return Helpers

# @pytest.mark.asyncio
# async def test_less_than_desired(helpers):
#     avg = 0.69
#     peak = 2.28
#     h = await helpers.setup_init_today_tomorrow()
#     _non = h.non_hours[:]
#     await h.async_update(avg, peak, 8)
#     assert h.total_charge == 8
#     assert len(h.non_hours) > len(_non)

# @pytest.mark.asyncio
# async def test_less_then_more(helpers):
#     avg = 0.69
#     peak = 2.28
#     h = await helpers.setup_init_today_tomorrow()
#     _non = h.non_hours[:]
#     await h.async_update(avg, peak, 8)
#     await h.async_update(avg, peak, 12)
#     assert h.total_charge == 12
#     assert len(h.non_hours) > len(_non)

# @pytest.mark.asyncio
# async def test_more_than_available(helpers):
#     avg = 0.69
#     peak = 2.28
#     h = await helpers.setup_init_today_tomorrow()
#     _non = h.non_hours[:]
#     await h.async_update(avg, peak, 100)
#     assert h.total_charge == 17.4
#     assert len(h.non_hours) == len(_non)


# @pytest.mark.asyncio
# async def test_lower_today(helpers):
#     avg = 0.69
#     peak = 2.28
#     h = await helpers.setup_init_today(mock_hour=0)
#     _non = [5,6,7,8,9, 10, 11, 12, 13]
#     initial = await h.async_initial_charge(avg, peak)
#     await h.async_update(avg, peak, 20)
#     assert h.total_charge == 20
#     await h.async_update(avg, peak, 100)
#     assert h.total_charge <= initial
