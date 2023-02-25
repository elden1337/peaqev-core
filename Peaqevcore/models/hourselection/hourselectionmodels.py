from dataclasses import dataclass, field
from typing import List, Dict
from .hourobject import HourObject
import logging

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=False)
class HoursModel:
    non_hours: List[int] = field(default_factory=lambda : [])
    caution_hours: List[int] = field(default_factory=lambda : [])
    dynamic_caution_hours: Dict[int, float] = field(default_factory=lambda : {})
    hours_today: HourObject = field(default_factory=lambda : HourObject([],[],dict()))
    hours_tomorrow: HourObject = field(default_factory=lambda : HourObject([],[],dict()))
    offset_dict: Dict[Dict[str,float], Dict[str, float]] = field(default_factory=lambda: {})

    def update_non_hours(
        self, 
        hour:int
        ) -> None:
        ret = []
        ret.extend(h for h in self.hours_today.nh if h >= hour)
        ret.extend(h for h in self.hours_tomorrow.nh if h < hour)
        self.non_hours = ret
    
    def update_caution_hours(
        self, 
        hour:int
        ) -> None:
        ret = []
        ret.extend(h for h in self.hours_today.ch if h >= hour)
        ret.extend(h for h in self.hours_tomorrow.ch if h < hour)
        self.caution_hours = ret

    def update_dynanmic_caution_hours(
        self, 
        hour:int
        ) -> None:
        ret = {}
        ret.update({k: v for k, v in self.hours_today.dyn_ch.items() if k >= hour and k not in self.hours_today.nh})
        ret.update({k: v for k, v in self.hours_tomorrow.dyn_ch.items() if k < hour and k not in self.hours_tomorrow.nh})
        self.dynamic_caution_hours = ret

    def update_offset_dict(self) -> None:
        ret = {}
        ret['today'] = self.hours_today.offset_dict
        ret['tomorrow'] = self.hours_tomorrow.offset_dict
        self.offset_dict = ret

@dataclass(frozen=False)
class HourSelectionOptions:
    cautionhour_type: float = 0
    top_price: float = 0
    min_price: float = 0
    absolute_top_price: float = field(init=False)

    def __post_init__(self):
        self.set_absolute_top_price(self.top_price, self.min_price)

    def set_absolute_top_price(self, top, min) -> None:
        if not self.validate_top_min_prices(top, min):
            top = 0
            HourSelectionOptions.min_price = 0
            _LOGGER.warning(f"Setting top-price and min-price to zero because of min-price being larger than top-price. Please fix in options. top:{top} min:{min}")
        if top is None:
            self.absolute_top_price = float("inf")
        elif top <= 0:
            self.absolute_top_price = float("inf")
        else:
            self.absolute_top_price = float(top)

    def validate_top_min_prices(self, top, min) -> bool:
        if any(
            [top == 0, min == 0]
        ):  
            return True
        return top > min
        

@dataclass(frozen=False)
class HourSelectionModel:
    prices_today: List[float] = field(default_factory=lambda : [])
    prices_tomorrow: List[float] = field(default_factory=lambda : [])
    adjusted_average: float = None
    current_peak: float = 0.0
    hours: HoursModel = HoursModel()
    options: HourSelectionOptions = HourSelectionOptions

    def __post_init__(self):
        self.validate()

    def validate(self):
        assert 0 < self.options.cautionhour_type <= 1
        assert isinstance(self.prices_today, list)
        assert isinstance(self.prices_tomorrow, list)

        if isinstance(self.adjusted_average, (int, float)):
            assert self.adjusted_average >= 0
        else:
            assert self.adjusted_average is None
        