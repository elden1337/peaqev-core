from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class MaxMinModel:
    input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    original_input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    total_charge: float = 0
    expected_hourly_charge: float = 0

    @property
    def average_price(self) -> float|None:
        try:
            print(self.input_hours)
            print(self.expected_hourly_charge)
            first = sum([v[0] * v[1] * self.expected_hourly_charge for k,v in self.input_hours.items() if v[1] > 0])
            return round(first/self.total_charge, 2)
        except ZeroDivisionError as e:
            return None