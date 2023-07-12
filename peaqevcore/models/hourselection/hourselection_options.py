from __future__ import annotations
from typing import TYPE_CHECKING

from ...models.hourselection.cautionhourtype import CautionHourType

import logging
from dataclasses import dataclass, field
from .topprice_type import TopPriceType
from .set_top_price import (
    set_absolute_top_price,
    async_add_tomorrow,
    async_validate_top_min_prices,
)

_LOGGER = logging.getLogger(__name__)

from datetime import datetime
from statistics import mean
from calendar import monthrange


@dataclass(frozen=False)
class HourSelectionOptions:
    cautionhour_type_enum: CautionHourType = CautionHourType.SUAVE
    top_price: float = 0  # move to separate file
    fixed_top_price: float = 0  # move to separate file
    dynamic_top_price: float = 0  # move to separate file
    top_price_type: TopPriceType = field(default_factory=lambda: TopPriceType.Unset)
    min_price: float = 0
    absolute_top_price: float = field(init=False)  # move to separate file

    def __post_init__(self):
        self.fixed_top_price = self.top_price
        (
            self.absolute_top_price,
            self.top_price_type,
            self.min_price,
        ) = set_absolute_top_price(self.min_price, self.top_price)

    async def async_add_tomorrow_to_top_price(
        self, prices_tomorrow: list, mock_day: int | None = None
    ) -> float:  # move to separate file
        _day = mock_day or datetime.now().day
        if _day + 1 > monthrange(datetime.now().year, datetime.now().month)[1]:
            """tomorrow is a new month so those prices should be calculated separately"""
            return mean(prices_tomorrow)
        if self.top_price_type != TopPriceType.Dynamic:
            return self.absolute_top_price
        return min(
            await async_add_tomorrow(_day, prices_tomorrow, self.absolute_top_price),
            self.absolute_top_price,
        )

    async def async_set_absolute_top_price(
        self, monthly_avg_top: float | None = None
    ) -> None:
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

        if not await async_validate_top_min_prices(top, _min):
            _LOGGER.warning(
                f"Setting top-price and min-price to zero because of min-price being larger than top-price. Please fix in options. top:{top} min:{_min}"
            )
            top = 0
            HourSelectionOptions.min_price = 0
        if top is None:
            self.absolute_top_price = float("inf")
        elif top <= 0:
            self.absolute_top_price = float("inf")
        else:
            self.absolute_top_price = float(top)
