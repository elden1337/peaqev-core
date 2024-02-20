from __future__ import annotations
from dataclasses import dataclass, field
from .models.seasoned_price import SeasonedPrice
from .models.tiered_price import TieredPrice
from ..enums.price_type import PriceType
from statistics import mean
import math

@dataclass
class LocalePrice:
    price_type: PriceType = field(default_factory=lambda: PriceType.Unset)
    value: float = 0.0
    _values: list[TieredPrice] | list[SeasonedPrice] | list = field(
        default_factory=lambda: []
    )
    currency: str = ""

    @property
    def is_active(self) -> bool:
        return self.price_type != PriceType.Unset

    def __post_init__(self):
        match self.price_type:
            case PriceType.Unset:
                pass
            case PriceType.Static:
                assert isinstance(self.value, (float, int))
                assert len(self.currency)
            case PriceType.Seasoned:
                assert isinstance(self._values[0], SeasonedPrice)
                assert len(self.currency)
            case PriceType.Tiered:
                assert isinstance(self._values[0], TieredPrice)
                assert len(self.currency)

    @property
    def price(self) -> float:
        match self.price_type:
            case PriceType.Static:
                return self.value
            case PriceType.Seasoned:
                return self._get_price_seasoned()
            case PriceType.Tiered:
                return self._get_price_tiered()
            case _:
                return 0.0

    def is_equal(self, other_currency: str) -> bool:
        """Use this method if necessary to test against the el-price currency"""
        return self.currency.lower == other_currency.lower

    def _get_price_seasoned(self) -> float:
        s: SeasonedPrice
        for s in [s for s in self._values if isinstance(s, SeasonedPrice)]:
            if s.validity.valid():
                return s.value

    def _get_price_tiered(self) -> float:
        for t in [s for s in self._values if isinstance(s, TieredPrice)]:
            pass

    def get_observed_peak(self, peaks: list[float], tiers: list[TieredPrice]) -> float:
        if self.price_type != PriceType.Tiered:
            return mean(peaks)
        
        limits = [tier.upper_peak_limit for tier in tiers]
        suggest = min(l for l in limits if l > mean(peaks)) - 0.1

        if len(peaks) == 1:
            return round(suggest,1)

        if all(p < suggest for p in peaks):
            return round(suggest,1)

        replaced_set = peaks
        
        for _ in range(50):
            min_count = replaced_set.count(min(replaced_set))
            
            if min_count == len(replaced_set):
                """All peaks have normalized. The suggest will suffice"""
                return round(suggest,1)
            
            if min_count == len(replaced_set) - 1:
                """All peaks have normalized except one. We can calculate the remainder"""
                return self._remainder_min(suggest, replaced_set)
            
            if replaced_set.count(max(replaced_set)) == len(replaced_set) - 1:
                """All peaks have normalized except one. We can calculate the remainder"""
                return self._remainder_max(suggest, replaced_set)
            
            replaced_set = self._count_up_min(suggest, replaced_set)
        return round(min(replaced_set),1)

    def _remainder_max(self, suggest: float, values: list[float]) -> float:
        remaining_difference = suggest * len(values) - sum(values)
        values = [round(p + remaining_difference, 2) if p < max(values) else p for p in values]
        return round(min(values),1)

    def _remainder_min(self, suggest: float, values: list[float]) -> float:
        needed_addition = (suggest * len(values) - sum(values)) / len(values)
        values = [min(round(p + needed_addition, 2), suggest) if p < suggest else p for p in values]
        remaining_difference = suggest * len(values) - sum(values)
        values = [min(round(p + remaining_difference / values.count(min(values)), 2), suggest) if p == min(values) else p for p in values]
        return round(min(values),1)

    def _count_up_min(self, suggest: float, values: list[float]) -> list:
        min_value = min(values)
        second_min_value = min(h for h in values if h > min_value)
        current_mean = sum(values) / len(values)
        min_count = values.count(min_value)

        addition = min(
            second_min_value - min_value,
            max(0.1, (suggest - current_mean) / min_count)
        )
        values = [round(p+addition,2) if p == min(values) else p for p in values]
        return values