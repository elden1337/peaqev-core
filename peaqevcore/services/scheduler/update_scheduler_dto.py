from dataclasses import dataclass, field

from peaqevcore.models.chargecontroller_states import ChargeControllerStates


@dataclass
class UpdateSchedulerDTO:
    moving_avg24: float
    peak: float
    chargecontroller_state: ChargeControllerStates
    charged_amount: float = 0.0
    prices: list|None = field(default_factory=lambda: None)
    prices_tomorrow: list|None = field(default_factory=lambda: None)
    charge_per_hour: float = field(init=False)

    def __post_init__(self):
        try:
            self.charge_per_hour = self.peak - (self.moving_avg24 / 1000)
        except Exception as e:
            self.charge_per_hour = 0.0