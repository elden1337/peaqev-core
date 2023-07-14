from dataclasses import dataclass, field
from typing import List
#from .hours_model import HoursModel
from .hourselection_options import HourSelectionOptions
import logging

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=False)
class HourSelectionModel:
    adjusted_average: float | None = None
    current_peak: float = 0.0
    options: HourSelectionOptions = field(
        default_factory=lambda: HourSelectionOptions()
    )

    def __post_init__(self):
        self.validate()

    def validate(self):
        if isinstance(self.adjusted_average, (int, float)):
            assert self.adjusted_average >= 0
        else:
            assert self.adjusted_average is None
