from dataclasses import dataclass, field
from .hour_price import HourPrice
from datetime import datetime
from statistics import mean

@dataclass
class MaxMinModel:
    min_price: float
    input_hours: list[HourPrice] = field(default_factory=lambda: [])
    expected_hourly_charge: float = 0

    def caluclate_average_price(
        self,
        input: list[HourPrice],
        total_charge: float | None,
        peak: float | None,
    ) -> float | None:
        #_total = total_charge or 0
        #_peak = peak or self.expected_hourly_charge
        result = [
                hp.price
                for hp in input
                if hp.permittance > 0 and not hp.passed
            ]
        if len(result):
            return round(mean(result),2)
        return 0.0

    def calculate_total_charge(self, input: list[HourPrice]) -> float:
        return round(
            sum(
                [
                    hp.permittance * self.expected_hourly_charge
                    for hp in input
                    if not hp.passed
                ]
            ),
            1,
        )
