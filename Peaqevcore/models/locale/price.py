from dataclasses import dataclass
from .enums.price_type import PriceType

class Tier:
    lower_peak_limit: float
    value: float


class TieredPrice:
    values: list[Tier]


@dataclass
class LocalePrice:
    price_type: PriceType
    value: float | TieredPrice
    currency:str

    def is_equal(self, other_currency: str) -> bool:
        """Use this method if necessary to test against the el-price currency"""
        return self.currency.lower == other_currency.lower


#if tiered, do a list of the tiers
    