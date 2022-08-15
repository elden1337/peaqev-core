from ast import Pow
import time
from .power_reading import PowerReading


class SessionPrice:
    def __init__(self) -> None:
        self._total_price: int = 0
        self._price: int = 0
        self._current_power: int = 0
        self._total_energy: float = 0
        self._current_time: int = 0
        self._time_delta: int = 0
        self._readings: list = []

    @property
    def total_energy(self) -> float:
        return round(self.get_status()["energy"]["value"], 3)

    def reset(self):
        self.__init__()

    def terminate(self, mock_time: float=None):
        print("called terminate")
        self.update_power_reading(0, mock_time)
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

    def update_session_pricing(self):
        if self._charger.session_is_active is False:
            self.core.terminate()