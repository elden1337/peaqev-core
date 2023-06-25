from dataclasses import dataclass, field
from .hour_price import HourPrice
from datetime import datetime


@dataclass
class MaxMinModel:
    min_price: float
    input_hours: list[HourPrice] = field(default_factory=lambda: [])
    original_input_hours: list[HourPrice] = field(default_factory=lambda: [])
    expected_hourly_charge: float = 0

    def caluclate_average_price(
        self, input: list[HourPrice], total_charge: float | None, dt: datetime
    ) -> float | None:
        _total = total_charge or 0
        _dt = dt.replace(minute=0, second=0, microsecond=0)
        try:
            first = sum(
                [
                    hp.permittance * hp.price * self.expected_hourly_charge
                    for hp in input
                    if hp.permittance > 0 and hp.dt >= _dt
                ]
            )
            return round(first / _total, 2)
        except ZeroDivisionError as e:
            return 0.0

    def calculate_total_charge(self, input: list[HourPrice], dt: datetime) -> float:
        _dt = dt.replace(minute=0, second=0, microsecond=0)
        return round(
            sum(
                [
                    hp.permittance * self.expected_hourly_charge
                    for hp in input
                    if hp.dt >= _dt
                ]
            ),
            1,
        )
