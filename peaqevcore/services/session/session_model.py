from dataclasses import dataclass, field


@dataclass
class SessionModel:
    total_price: float = 0
    price: float = 0
    current_power: float = 0
    total_energy: float = 0
    current_time: float = 0
    time_delta: float = 0
    readings: list = field(default_factory=lambda: [])
