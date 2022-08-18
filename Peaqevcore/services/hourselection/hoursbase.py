from dataclasses import dataclass, field
from datetime import datetime
from abc import abstractmethod
from .const import NON_HOUR, CAUTION_HOUR, CHARGING_PERMITTED

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
    def non_hours(self):
        return self._non_hours

    @non_hours.setter
    def non_hours(self, val):
        self._non_hours = val

    @property
    def caution_hours(self):
        return self._caution_hours

    @caution_hours.setter
    def caution_hours(self, val):
        self._caution_hours = val

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

# @dataclass
# class Hours:
#     price_aware: bool
#     non_hours: list = None
#     caution_hours: list = None

#     @property
#     def state(self) -> str:
#         if datetime.now().hour in self.non_hours:
#             return NON_HOUR
#         if datetime.now().hour in self.caution_hours:
#             return CAUTION_HOUR
#         return CHARGING_PERMITTED

#     @property
#     @abstractmethod
#     def nordpool_entity(self):
#         pass

#     @abstractmethod
#     def update_nordpool(self) -> None:
#         pass

#     @property
#     @abstractmethod
#     def dynamic_caution_hours(self) -> dict:
#         pass

#     @property
#     @abstractmethod
#     def options(self):
#         pass