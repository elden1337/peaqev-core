import logging
from dataclasses import dataclass, field
from .topprice_type import TopPriceType

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=False)
class HourSelectionOptions:
    cautionhour_type: float = 0
    top_price: float = 0
    fixed_top_price: float = 0
    dynamic_top_price: float = 0
    top_price_type: TopPriceType = TopPriceType.Unset
    min_price: float = 0
    blocknocturnal: bool = False
    absolute_top_price: float = field(init=False)

    def __post_init__(self):
        self.set_absolute_top_price()

    def set_absolute_top_price(self) -> None:
        _min = self.min_price
        top = self.top_price
        self.fixed_top_price = self.top_price
        
        if not self.validate_top_min_prices(top, _min):
            _LOGGER.warning(f"Setting top-price and min-price to zero because of min-price being larger than top-price. Please fix in options. top:{top} min:{_min}")
            top = 0
            HourSelectionOptions.min_price = 0
        if top is None:
            self.absolute_top_price = float("inf")
            self.top_price_type = TopPriceType.Unset
        elif top <= 0:
            self.absolute_top_price = float("inf")
            self.top_price_type = TopPriceType.Unset
        else:
            self.absolute_top_price = float(top)
            self.top_price_type = TopPriceType.Absolute

    def validate_top_min_prices(self, top, min) -> bool:
        if any(
            [top == 0, min == 0]
        ):  
            return True
        return top > min

    async def async_set_absolute_top_price(self, monthly_avg_top:float=None) -> None:
        _min = self.min_price
        self.fixed_top_price = self.top_price
        if monthly_avg_top is None:
            top = self.top_price
        else:
            self.dynamic_top_price = monthly_avg_top
            top = min(monthly_avg_top, self.top_price)
            if monthly_avg_top <= self.top_price:
                self.top_price_type = TopPriceType.Dynamic
            else:
                self.top_price_type = TopPriceType.Absolute

        if not await self.async_validate_top_min_prices(top, _min):
            _LOGGER.warning(f"Setting top-price and min-price to zero because of min-price being larger than top-price. Please fix in options. top:{top} min:{_min}")
            top = 0
            HourSelectionOptions.min_price = 0
        if top is None:
            self.absolute_top_price = float("inf")
        elif top <= 0:
            self.absolute_top_price = float("inf")
        else:
            self.absolute_top_price = float(top)

    async def async_validate_top_min_prices(self, top, min) -> bool:
        if any(
            [top == 0, min == 0]
        ):  
            return True
        return top > min