
from dataclasses import dataclass, field
from .savings_status import SavingsStatus
from datetime import date, datetime

@dataclass
class SavingsModel:
    prices: dict[date, list[float]] = field(default_factory=lambda: {})
    registered_consumption: dict[date, list[float]] = field(default_factory=lambda: {})
    peaks: dict[date, list[float]] = field(default_factory=lambda: {})
    peak_price_per_kwh: float = field(init=False)
    status: SavingsStatus = SavingsStatus.Off

    def __post_init__(self) -> None:
        self.peaks_price_per_kwh = 1

    async def add_prices(self, prices:list[float]) -> None:
        self.prices[date.today()] = prices

    async def add_to_registered_consumption(self, registered_consumption:float, hour:int = datetime.now().hour) -> None:        
        self.registered_consumption[date.today()][hour] +=registered_consumption

    async def add_to_peaks(self, peak:float, hour:int = datetime.now().hour) -> None:
        self.peaks[date.today()][hour] += peak