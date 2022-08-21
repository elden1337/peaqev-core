from dataclasses import dataclass
from .enums import PriceType

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




#if tiered, do a list of the tiers
    