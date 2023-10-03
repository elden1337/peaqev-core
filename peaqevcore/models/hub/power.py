import logging

from ...util import nametoid
from ...models.const import DOMAIN
from .hubmember import HubMember
from ...hub.killswitch import KillSwitch
from .const import TOTALPOWER, HOUSEPOWER

_LOGGER = logging.getLogger(__name__)


class Power:
    def __init__(self, configsensor: str, powersensor_includes_car: bool = False):
        self._config_sensor = configsensor
        self._total = HubMember(data_type=int, initval=0, name=TOTALPOWER)
        self._house = HubMember(data_type=int, initval=0, name=HOUSEPOWER)
        self._powersensor_includes_car = powersensor_includes_car
        self.killswitch = KillSwitch(
            sensor=self._config_sensor, update_interval=120, grace_interval=300
        )
        self._setup()

    @property
    def is_initialized(self) -> bool:
        return self._total.is_initialized and self._house.is_initialized

    @property
    def config_sensor(self) -> str:
        return self._config_sensor

    @property
    def total(self) -> HubMember:
        self.killswitch.check
        return self._total

    @total.setter
    def total(self, val):
        self._total = val

    @property
    def house(self) -> HubMember:
        self.killswitch.check
        return self._house

    @house.setter
    def house(self, val):
        self._house = val

    @property
    def car_power(self) -> int:
        try:
            ret = int(self._total.value - self._house.value) #type: ignore
            return max(0, ret)
        except:
            return 0

    def _setup(self):
        if self._powersensor_includes_car is True:
            self.total.entity = self.config_sensor
            self.house.entity = nametoid(f"sensor.{DOMAIN}_{HOUSEPOWER}")
        else:
            self.house.entity = self._config_sensor

    async def async_update(self, carpowersensor_value=0, config_sensor_value=None):
        self.update(carpowersensor_value, config_sensor_value)

    def update(self, carpowersensor_value=0, config_sensor_value=None):
        if not isinstance(carpowersensor_value, float|int):
            _LOGGER.warning(
                f"Power.update called with invalid value: {carpowersensor_value}"
            )
            return
        
        if self._powersensor_includes_car is True:
            if config_sensor_value is not None:
                self.total.value = config_sensor_value
            new_val = float(self.total.value) - float(carpowersensor_value) #type: ignore
            if new_val != self.house.value:
                self.killswitch.update()
            self.house.value = new_val
        else:
            if config_sensor_value is not None:
                self.house.value = config_sensor_value
            new_val = float(self.house.value) + float(carpowersensor_value) #type: ignore
            if new_val != self.total.value:
                self.killswitch.update()
            self.total.value = new_val
