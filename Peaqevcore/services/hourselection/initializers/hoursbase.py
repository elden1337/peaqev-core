from dataclasses import dataclass, field
from datetime import datetime
from abc import abstractmethod
from ..const import NON_HOUR, CAUTION_HOUR, CHARGING_PERMITTED

class Hours:
    def __init__(
            self,
            price_aware: bool,
            non_hours: list = None,
            caution_hours: list = None
    ):
        self._non_hours = non_hours
        self._caution_hours = caution_hours
        self._price_aware = price_aware
        self._is_initialized = False

    @property
    def state(self) -> str:
        if datetime.now().hour in self.non_hours:
            return NON_HOUR
        if datetime.now().hour in self.caution_hours:
            return CAUTION_HOUR
        return CHARGING_PERMITTED

    @property
    def price_aware(self) -> bool:
        return self._price_aware

    @property
    @abstractmethod
    def non_hours(self):
        pass

    @property
    @abstractmethod
    def is_initialized(self):
        pass

    @non_hours.setter
    @abstractmethod
    def non_hours(self, val):
        pass

    @property
    @abstractmethod
    def caution_hours(self):
        pass

    @caution_hours.setter
    @abstractmethod
    def caution_hours(self, val):
        pass

    @property
    @abstractmethod
    def nordpool_entity(self):
        pass

    @abstractmethod
    def update_nordpool(self) -> None:
        pass

    @property
    @abstractmethod
    def dynamic_caution_hours(self) -> dict:
        pass

    @property
    @abstractmethod
    def options(self):
        pass

    @property
    @abstractmethod
    def offsets(self) -> dict:
        pass