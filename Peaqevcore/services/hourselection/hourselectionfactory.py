from ...hub.hub import HubBase
from .price_aware_hours import PriceAwareHours
from .regular_hours import RegularHours

class HourselectionFactory:
    @staticmethod
    def create(hubbase: HubBase):
        if hubbase.hub.price_aware is False:
            return RegularHours(hubbase.hub)
        return PriceAwareHours(hubbase.hub)