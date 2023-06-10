from dataclasses import dataclass, field
from .savings_status import SavingsStatus
from datetime import date, datetime
from .consumption_model import ConsumptionModel
import logging

_LOGGER = logging.getLogger(__name__)


@dataclass
class SavingsModel(ConsumptionModel):
    peak_price_per_kwh: float = 0
    car_connected_at: datetime | None = None
    prices: dict[date, list[float]] = field(default_factory=lambda: {})
    status: SavingsStatus = field(default_factory=lambda: SavingsStatus.Off)

    async def async_reset(self) -> None:
        self.status = SavingsStatus.Off
        self.prices = {}
        self.consumption = {}
        # self.peaks = {}

    async def async_re_initialize(self, incoming: dict):
        self.car_connected_at = incoming.get("car_connected_at", None)
        self.prices = incoming.get("prices", {})
        self.consumption = incoming.get("consumption", {})
        if all(
            [
                self.car_connected_at is not None,
                len(self.prices) > 0,
                len(self.consumption) > 0,
            ]
        ):
            self.status = SavingsStatus.Collecting
        else:
            _LOGGER.warning("Cannot re-initialize SavingsModel, missing data")

    async def async_add_prices(
        self, prices: list[float], _date: date | None = None
    ) -> None:
        if _date is None:
            _date = datetime.now().date()
        self.prices[_date] = prices

    async def async_add_to_consumption(
        self,
        consumption: float,
        date: date | None = None,
        hour: int | None = None,
    ) -> None:
        if self.status is not SavingsStatus.Collecting:
            return
        await self.async_add_consumption(consumption, date, hour)
