from datetime import datetime
import pytest

from ..scheduler_service.scheduler import Scheduler

MOCKPRICES = [0.422, 0.341, 0.309, 0.322, 0.331, 0.422, 0.773, 1.169, 1.794, 1.975, 2.119, 1.849, 1.309, 1.24, 1.137, 1.122, 1.14, 1.3, 1.397, 1.971, 1.377, 1.178, 1.05, 0.709]
MOCKPRICES_TOMORROW = [0.513, 0.452, 0.458, 0.413, 0.377, 0.498, 0.693, 2.145, 2.193, 2.191, 2.184, 2.168, 2.153, 2.144, 2.135, 2.12, 2.134, 2.156, 2.165, 2.159, 2.146, 2.121, 2.081, 0.983]

def test_scheduler_overnight_1():
    s = Scheduler()
    MOCKDT = datetime.strptime('22-07-20 19:00', '%y-%m-%d %H:%M')
    dep_time_obj = datetime.strptime('22-07-21 06:00', '%y-%m-%d %H:%M')
    s.create(desired_charge=11, departuretime=dep_time_obj, starttime=MOCKDT)
    s.update(avg24=710, peak=4.71, charged_amount=0, prices=MOCKPRICES, prices_tomorrow=MOCKPRICES_TOMORROW,mockdt=dep_time_obj)
    assert s.model.non_hours == [19,20,21,22,23,0,1,5]
    assert s.model.hours_charge == {datetime(2022, 7, 21, 2, 0): 1, datetime(2022, 7, 21, 3, 0): 1, datetime(2022, 7, 21, 4, 0): 0.7}