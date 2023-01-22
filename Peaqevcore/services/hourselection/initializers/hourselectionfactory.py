from .price_aware_hours import PriceAwareHours
from .regular_hours import RegularHours

class HourselectionFactory:
    @staticmethod
    def create(hub):
        if hub.options.price.price_aware is False:
            return RegularHours(hub)
        return PriceAwareHours(hub)