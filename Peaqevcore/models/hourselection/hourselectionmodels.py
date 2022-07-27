from dataclasses import dataclass, field
from typing import List, Dict
from .hourobject import HourObject

@dataclass(frozen=False)
class HoursModel:
    non_hours: List[int] = field(default_factory=lambda : [])
    caution_hours: List[int] = field(default_factory=lambda : [])
    dynamic_caution_hours: Dict[int, float] = field(default_factory=lambda : {})
    hours_today: HourObject = field(default_factory=lambda : HourObject([],[],dict()))
    hours_tomorrow: HourObject = field(default_factory=lambda : HourObject([],[],dict()))


@dataclass(frozen=False)
class HourSelectionOptions:
    cautionhour_type: float = 0
    absolute_top_price: float = 0
    min_price: float = 0
    allow_top_up: bool = False


@dataclass(frozen=False)
class HourSelectionModel:
    prices_today: List[float] = field(default_factory=lambda : [])
    prices_tomorrow: List[float] = field(default_factory=lambda : [])
    hours: HoursModel = HoursModel()
    options: HourSelectionOptions = HourSelectionOptions