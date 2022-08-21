import logging
from .hoursbase import Hours
from .hoursselection import Hoursselection as core_hours
from ...models.hourselection.const import (CAUTIONHOURTYPE_INTERMEDIATE, CAUTIONHOURTYPE_SUAVE, CAUTIONHOURTYPE_AGGRESSIVE, CAUTIONHOURTYPE
)

_LOGGER = logging.getLogger(__name__)


class PriceAwareHours(Hours):
    def __init__(
            self,
            hub
    ):
        self._hub = hub
        self._cautionhour_type = CAUTIONHOURTYPE[hub.options.price.cautionhour_type]
        self._cautionhour_type_string = hub.options.price.cautionhour_type
        self._core = core_hours(
            self._set_absolute_top_price(hub.options.price.top_price),
            hub.options.price.min_price,
            self._cautionhour_type, hub.options.price.allow_top_up
        )
        self._hass = hub.state_machine
        self._prices = []
        self._is_initialized = False
        super().__init__(price_aware=True)

    @property
    def options(self):
        return self._core.options

    @property
    def dynamic_caution_hours(self) -> dict:
        return self._core.dynamic_caution_hours

    @property
    def cautionhour_type_string(self) -> str:
        return self._cautionhour_type_string

    @property
    def non_hours(self) -> list:
        return self._core.non_hours

    @non_hours.setter
    def non_hours(self, val):
        pass

    @property
    def caution_hours(self) -> list:
        return self._core.caution_hours

    @caution_hours.setter
    def caution_hours(self, val):
        pass

    @property
    def absolute_top_price(self):
        return self._core.options.absolute_top_price

    @property
    def min_price(self):
        return self._core.options.min_price

    @property
    def prices(self) -> list:
        return self._core.prices

    @prices.setter
    def prices(self, val):
        self._core.prices = val

    @property
    def prices_tomorrow(self) -> list:
        return self._core.prices_tomorrow

    @prices_tomorrow.setter
    def prices_tomorrow(self, val):
        self._core.prices_tomorrow = val

    @property
    def is_initialized(self) -> bool:
        if self.prices is not None:
            if len(self.prices) > 0:
                if self._is_initialized is False:
                    self._is_initialized = True
                    _LOGGER.debug("Hourselection has initialized")
                return True
        return False

    def get_average_kwh_price(self):
        #if self._is_initialized:
        try:
            return self._core.get_average_kwh_price()
        except ZeroDivisionError as e:
            _LOGGER.warning(e)
        return 0

    def get_total_charge(self):
        #if self._is_initialized:
        try:
            return self._core.get_total_charge(self._hub.sensors.current_peak.value)
        except ZeroDivisionError as e:
            _LOGGER.warning(e)
        return 0

    @staticmethod
    def _set_absolute_top_price(_input) -> float:
        if _input is None or _input <= 0:
            return float("inf")
        return _input