from ...hub.hub_options import HubOptions
from .price_aware_hours import PriceAwareHours
from .regular_hours import RegularHours

class HourselectionFactory:
    @staticmethod
    def create(huboptions: HubOptions):
        if huboptions.price_aware is False:
            return RegularHours(huboptions)
        return PriceAwareHours(huboptions)