from .hoursbase import Hours
from datetime import datetime, timedelta


class RegularHours(Hours):
    def __init__(self, hub):
        self.hub = hub
        self.timer = None
        self.scheduler = None
        super().__init__(
            False, self.hub.options.nonhours, self.hub.options.cautionhours
        )

    @property
    def non_hours(self):
        return self.create_hours(self._non_hours)

    @non_hours.setter
    def non_hours(self, val):
        self._non_hours = val

    @property
    def caution_hours(self):
        return self.create_hours(self._caution_hours)

    @caution_hours.setter
    def caution_hours(self, val):
        self._caution_hours = val

    @property
    def is_initialized(self) -> bool:
        return True

    async def async_update_max_min(
        self,
        max_charge: float,
        session_energy: float | None = None,
        car_connected: bool = False,
        limiter: float = 0.0
    ):
        pass

    @property
    def absolute_top_price(self):
        return None

    @property
    def min_price(self):
        return None

    @property
    def future_hours(self) -> list: #type: ignore
        pass

    def create_hours(self, input:list = []) -> list[datetime]:
        hours = []
        for hour in input:
            if hour < datetime.now().hour:
                hours.append(datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(days=1))
            else:
                hours.append(datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0))
        return hours