from dataclasses import dataclass, field
from .hour_price import HourPrice


@dataclass
class HourSelectionModel:
    prices_today: list[float] = field(default_factory=list)
    prices_tomorrow: list[float] = field(default_factory=list)
    hours_prices: list[HourPrice] = field(default_factory=list)
    adjusted_average: float | None = None
