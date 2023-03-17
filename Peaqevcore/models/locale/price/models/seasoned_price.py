from dataclasses import dataclass
from .....services.locale.time_pattern import TimePattern

@dataclass
class SeasonedPrice:
    validity: TimePattern
    value: float

    def __post_init__(self):
        assert self.value >= 0