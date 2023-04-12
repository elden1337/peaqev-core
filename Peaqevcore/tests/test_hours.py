import pytest
import statistics as stat
from ..services.hourselection.initializers.regular_hours import RegularHours
from ..services.hourselection.initializers.price_aware_hours import PriceAwareHours
#from ..models.hourselection.cautionhourtype import CautionHourType


class MockOptions:
    def __init__(self, nonhours, cautionhours):
        self.nonhours = nonhours
        self.cautionhours = cautionhours

class MockHub:
    def __init__(self, options):
        self.options = options


def test_regular_hours_non_initialized():
    options = MockOptions([0,1,2], [23])
    hub = MockHub(options)
    h = RegularHours(hub)
    
    assert h.is_initialized == True
    assert hasattr(h, 'timer') == True
    assert hasattr(h, 'scheduler') == True




