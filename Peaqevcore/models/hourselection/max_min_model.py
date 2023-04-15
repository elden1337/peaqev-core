from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class MaxMinModel:
    input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    original_input_hours: dict[int, Tuple[float, float]] = field(default_factory=lambda: {})
    total_charge: float = 0
        
    @property
    def average_price(self) -> float|None:
        try:
            return round(sum([v[0] * v[1] for k,v in self.input_hours.items() if v[1] > 0])/self.total_charge,1)
        except ZeroDivisionError as e:
            return None
    
        
