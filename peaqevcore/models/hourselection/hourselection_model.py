from dataclasses import dataclass, field
from typing import List
#from .hours_model import HoursModel
from .hourselection_options import HourSelectionOptions
import logging

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=False)
class HourSelectionModel:
    #prices_today: List[float] = field(default_factory=lambda: [])
    #prices_tomorrow: List[float] = field(default_factory=lambda: [])
    adjusted_average: float | None = None
    current_peak: float = 0.0
    options: HourSelectionOptions = field(
        default_factory=lambda: HourSelectionOptions()
    )

    def __post_init__(self):
        self.validate()

    def validate(self):
        #assert isinstance(self.prices_today, list)
        #assert isinstance(self.prices_tomorrow, list)

        if isinstance(self.adjusted_average, (int, float)):
            assert self.adjusted_average >= 0
        else:
            assert self.adjusted_average is None
