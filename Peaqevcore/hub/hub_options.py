from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Price:
    price_aware: bool = False
    allow_top_up: bool = False
    min_price: float = 0.0
    top_price: float = 0.0
    cautionhour_type: str = ""

@dataclass
class HubOptions:
    locale: str = field(init=False)
    chargertype: str = field(init=False)
    chargerid: str = field(init=False)
    price: Price = Price()
    peaqev_lite: bool = False
    powersensor_includes_car: bool = False
    powersensor: str = field(init=False)
    behavior_on_default: bool = False
    startpeaks: dict = field(default_factory=dict)
    cautionhours: List = field(default_factory=lambda: [])
    nonhours: List = field(default_factory=lambda: [])

