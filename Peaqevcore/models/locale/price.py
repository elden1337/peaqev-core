from __future__ import annotations
from dataclasses import dataclass
from ...services.locale.time_pattern import TimePattern
from .enums.price_type import PriceType

@dataclass
class TieredPrice:
    lower_peak_limit: float
    value: float

    def __post_init__(self):
        assert self.value >= 0
        assert self.lower_peak_limit >= 0


@dataclass
class SeasonedPrice:
    validity: TimePattern
    value: float

    def __post_init__(self):
        assert self.value >= 0


@dataclass
class LocalePrice:
    price_type: PriceType
    value: float | list[TieredPrice] | list[SeasonedPrice]
    currency:str

    def __post_init__(self):
        match self.price_type:
            case PriceType.Static:
                assert isinstance(self.value, (float,int))
            case PriceType.Seasoned:
                assert type(self.value) == list
                assert isinstance(self.value[0], SeasonedPrice)
            case PriceType.Tiered:
                assert type(self.value) == list
                assert isinstance(self.value[0], TieredPrice)
        assert len(self.currency) > 0

    @property
    def price(self) -> float:
        match self.price_type:
            case PriceType.Static:
                return self.value
            case PriceType.Seasoned:
                return self._get_price_seasoned()
            case PriceType.Tiered:
                return self._get_price_tiered()

    def is_equal(self, other_currency: str) -> bool:
        """Use this method if necessary to test against the el-price currency"""
        return self.currency.lower == other_currency.lower

    def _get_price_seasoned(self) -> float:
        s: SeasonedPrice
        for s in self.value:
            if s.validity.valid():
                return s.value        

    def _get_price_tiered(self):
        t: TieredPrice
        for t in self.value:
            pass
    

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
