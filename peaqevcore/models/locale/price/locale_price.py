from __future__ import annotations
from dataclasses import dataclass, field
from .models.seasoned_price import SeasonedPrice
from .models.tiered_price import TieredPrice
from ..enums.price_type import PriceType

@dataclass
class LocalePrice:
    price_type: PriceType = field(default_factory=lambda: PriceType.Unset)
    value: float = 0.0
    _values: list[TieredPrice] | list[SeasonedPrice] | list = field(default_factory=lambda: [])
    currency: str = ""

    @property
    def is_active(self) -> bool:
        return self.price_type != PriceType.Unset

    def __post_init__(self):
        self.currency = self.currency.upper()
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
        return self.value

    def _get_price_tiered(self) -> float:
        for t in [s for s in self._values if isinstance(s, TieredPrice)]:
            pass
        return self.value
