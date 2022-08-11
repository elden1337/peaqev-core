from dataclasses import dataclass, field

@dataclass
class HubOptions:
    price_aware: bool = False
    peaqev_lite: bool = False
    powersensor_includes_car: bool = False

