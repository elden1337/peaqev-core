from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class MaxMinModel:
    min_price: float
    input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    original_input_hours: dict[int, Tuple[float, float]] = field(
        default_factory=lambda: {}
    )
    expected_hourly_charge: float = 0

    @property
    def average_price(self) -> float | None:
        return self._caluclate_average_price(
            self.input_hours, self.total_charge, self.expected_hourly_charge
        )

    @property
    def original_average_price(self) -> float | None:
        return self._caluclate_average_price(
            self.original_input_hours,
            self.original_total_charge,
            self.expected_hourly_charge,
        )

    @property
    def total_charge(self) -> float:
        return self._calculate_total_charge(
            self.input_hours, self.expected_hourly_charge
        )

    @property
    def original_total_charge(self) -> float:
        return self._calculate_total_charge(
            self.original_input_hours, self.expected_hourly_charge
        )

    @staticmethod
    def _caluclate_average_price(
        input: dict, total_charge: float, expected: float
    ) -> float | None:
        try:
            first = sum([v[0] * v[1] * expected for k, v in input.items() if v[1] > 0])
            return round(first / total_charge, 2)
        except ZeroDivisionError as e:
            return None

    @staticmethod
    def _calculate_total_charge(input: dict, expected: float) -> float:
        ret = sum([v[1] * expected for k, v in input.items()])
        return round(ret, 1)
