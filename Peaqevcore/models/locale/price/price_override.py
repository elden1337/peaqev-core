from .locale_price import LocalePrice

class PriceOverride:
    """When to override peaks"""
    def __init__(self, price:LocalePrice) -> None:
        self._price = price
        pass

    #if tiered price we should obv allow up to just below the next level.

    @property
    def increase(self) -> float:
        #get current peakprice
        #get current nordpool price
        #get nordpool avg7
        #get nordpool prognosis for today and tomorrow
        #get length of current period (how far along are we)
        #calculate and return a number on how much to increase peak
        return 0.0