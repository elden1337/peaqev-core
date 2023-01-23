from __future__ import annotations
from dataclasses import dataclass
from ...services.locale.time_pattern import TimePattern
from .enums.price_type import PriceType

@dataclass
class TieredPrice:
    lower_peak_limit: float
    value: float

@dataclass
class SeasonedPrice:
    validity: TimePattern
    value: float

@dataclass
class LocalePrice:
    price_type: PriceType
    value: float | list[TieredPrice] | list[SeasonedPrice]
    currency:str

    def is_equal(self, other_currency: str) -> bool:
        """Use this method if necessary to test against the el-price currency"""
        return self.currency.lower == other_currency.lower

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

#if tiered, do a list of the tiers
    