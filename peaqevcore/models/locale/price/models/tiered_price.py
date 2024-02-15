from dataclasses import dataclass

@dataclass
class TieredPrice:
    upper_peak_limit: float
    value: float

    def __post_init__(self):
        assert self.value >= 0
        assert self.upper_peak_limit >= 0