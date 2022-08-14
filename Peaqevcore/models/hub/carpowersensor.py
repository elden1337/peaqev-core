import logging
from ...util import try_parse
from .hubmember import HubMember
from .const import CARPOWERSENSOR

_LOGGER = logging.getLogger(__name__)


class CarPowerSensor(HubMember):
    def __init__(
            self,
            data_type: type,
            listenerentity=None,
            initval=None,
            powermeter_factor=1,
            hubdata=None
    ):
        self._hubdata = hubdata
        self._powermeter_factor = powermeter_factor
        self._warned_not_initialized = False
        self._is_initialized = False
        super().__init__(data_type, listenerentity, initval)

    @property
    def is_initialized(self) -> bool:
        if self._is_initialized is True:
            return True
        if isinstance(self.value, (float,int)) and self._hubdata.chargerobject.is_initialized:
            _LOGGER.debug(f"{CARPOWERSENSOR} has initialized")
            self._is_initialized = True
            return True
        return False

    @HubMember.value.setter
    def value(self, val):
        if val is None or val == 0:
            self._value = 0
        vval = try_parse(val, float)
        if not vval:
            vval = try_parse(val, int)
        if not vval:
            self._value = 0
        else:
            self._value = float(vval * self._powermeter_factor)


