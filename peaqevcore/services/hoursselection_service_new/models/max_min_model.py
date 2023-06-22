from dataclasses import dataclass, field
from .hour_price import HourPrice


@dataclass
class MaxMinModel:
    min_price: float
    input_hours: list[HourPrice] = field(default_factory=lambda: [])
    original_input_hours: list[HourPrice] = field(default_factory=lambda: [])
    expected_hourly_charge: float = 0

    @property
    def average_price(self) -> float | None:
        return self._caluclate_average_price(
            self.input_hours, self.total_charge, self.expected_hourly_charge
        )

    @property
    def total_charge(self) -> float:
        return self._calculate_total_charge(
            self.input_hours, self.expected_hourly_charge
        )

    @staticmethod
    def _caluclate_average_price(
        input: list[HourPrice], total_charge: float, expected: float
    ) -> float | None:
        try:
            first = sum(
                [
                    hp.permittance * hp.price * expected
                    for hp in input
                    if hp.permittance > 0
                ]
            )
            return round(first / total_charge, 2)
        except ZeroDivisionError as e:
            return None

    @staticmethod
    def _calculate_total_charge(input: list[HourPrice], expected: float) -> float:
        return round(sum([hp.permittance * expected for hp in input]), 1)
