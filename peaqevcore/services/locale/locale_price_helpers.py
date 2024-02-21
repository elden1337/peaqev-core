from statistics import mean
from ...models.locale.price.models.tiered_price import TieredPrice
from ...models.locale.enums.price_type import PriceType

def get_observed_peak(price_type: PriceType, peaks: list[float], tiers: list[TieredPrice]) -> float:
        if price_type != PriceType.Tiered:
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
                return _remainder_min(suggest, replaced_set)
            
            if replaced_set.count(max(replaced_set)) == len(replaced_set) - 1:
                """All peaks have normalized except one. We can calculate the remainder"""
                return _remainder_max(suggest, replaced_set)
            
            replaced_set = _count_up_min(suggest, replaced_set)
        return round(min(replaced_set),1)

def _remainder_max(suggest: float, values: list[float]) -> float:
    remaining_difference = suggest * len(values) - sum(values)
    values = [round(p + remaining_difference, 2) if p < max(values) else p for p in values]
    return round(min(values),1)

def _remainder_min(suggest: float, values: list[float]) -> float:
    needed_addition = (suggest * len(values) - sum(values)) / len(values)
    values = [min(round(p + needed_addition, 2), suggest) if p < suggest else p for p in values]
    remaining_difference = suggest * len(values) - sum(values)
    values = [min(round(p + remaining_difference / values.count(min(values)), 2), suggest) if p == min(values) else p for p in values]
    return round(min(values),1)

def _count_up_min(suggest: float, values: list[float]) -> list:
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