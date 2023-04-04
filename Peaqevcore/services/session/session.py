import time
from .power_reading import PowerReading
from .energy_weekly import EnergyWeekly
import logging

_LOGGER = logging.getLogger(__name__)


class SessionPrice:
    def __init__(self, init_average_data = None) -> None:
        self._total_price: int = 0
        self._price: int = 0
        self._current_power: int = 0
        self._total_energy: float = 0
        self._current_time: int = 0
        self._time_delta: int = 0
        self._readings: list = []
        self.average_data = EnergyWeekly(init_average_data)

    @property
    def energy_average(self) -> float:
        return self.average_data.average

    @property
    def energy_weekly_dict(self) -> dict:
        return self.average_data.export

    @property
    def total_energy(self) -> float:
        return round(self.get_status()["energy"]["value"], 3)

    def reset(self): #add inputparams here
        #push a heartbeat to the api
        self.__init__(self.average_data.export)

    def terminate(self, mock_time: float=None):
        self.update_power_reading(0, mock_time)
        _LOGGER.debug(f"Called terminate on session_price. Trying to add {self.total_energy} to statistics.")
        self.average_data.update(self.total_energy, mock_time)
        self.get_status()

    def set_status(self) -> None:
        for i in self._readings:
            self._total_energy += i.reading_integral
            self._total_price += i.reading_cost

    def get_status(self) -> dict:
        self._total_energy = 0
        self._total_price = 0
        self.set_status()
        return {
            "energy": {
                "value": self._total_energy,
                "unit": "kWh"
            },
            "price": self._total_price
        }

    def update_power_reading(self, power: any, mock_time: float=None):
        self._set_delta(mock_time)
        p = PowerReading(self._price, self._current_power, self._time_delta)
        self._readings.append(p)
        try:
            self._current_power = float(power)
        except:
            self._current_power = 0

    def update_price(self, price: any, mock_time: float=None):
        if self._current_power > 0:
            self.update_power_reading(
                power=self._current_power,
                mock_time=mock_time
            )
        try:
            self._price = float(price)
        except:
            self._price = 0

    def _set_delta(self, mock_time: float=None) -> None:
        now = mock_time or time.time()
        self._time_delta = (now - self._current_time)
        self._current_time = now

    @property
    def readings(self) -> list:
        return self._readings

    @property
    def total_price(self) -> float:
        return round(self.get_status()["price"], 3)

    @total_price.setter
    def total_price(self, val):
        self.total_price = val


class Session:
    def __init__(self, charger):
        self._charger = charger
        self.core = SessionPrice()
        self.core._set_delta()

    @property
    def session_energy(self):
        return self.core.total_energy

    @session_energy.setter
    def session_energy(self, val):
        self.core.update_power_reading(val)
        self.update_session_pricing()

    @property
    def session_price(self):
        return self.core.total_price

    @session_price.setter
    def session_price(self, val):
        self.core.update_price(val)
        self.update_session_pricing()

    @property
    def energy_average(self) -> float:
        return self.core.energy_average

    @property
    def energy_weekly_dict(self) -> dict:
        return self.core.energy_weekly_dict

    def update_session_pricing(self):
        if self._charger.model.session_active is False:
            self.core.terminate()