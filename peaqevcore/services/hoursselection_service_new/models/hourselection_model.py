from dataclasses import dataclass, field
from .hour_price import HourPrice


@dataclass
class HourSelectionModel:
    prices_today: list[float] = field(default_factory=list)
    prices_tomorrow: list[float] = field(default_factory=list)
    _hours_prices: list[HourPrice] = field(default_factory=list)
    adjusted_average: float | None = None

    @property
    def hours_prices(self) -> list[HourPrice]:
        return self._hours_prices

    @hours_prices.setter
    def hours_prices(self, val: list[HourPrice]) -> None:
        self._hours_prices = sort(val, key=lambda x: x.dt)