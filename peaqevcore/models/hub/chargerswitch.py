import logging
from .hubmember import HubMember

_LOGGER = logging.getLogger(__name__)


class ChargerSwitch(HubMember):
    def __init__(
            self,
            hass,
            data_type: type,
            listenerentity,
            initval,
            currentname: str,
            hubdata=None,
            init_override:bool = False
    ):
        self._hubdata = hubdata
        self._hass = hass
        self._value = initval
        self._current = None
        self._current_attr_name = currentname
        super().__init__(data_type=data_type, listenerentity=listenerentity, init_override=init_override, initval=initval, hass=hass)

    @property
    def is_initialized(self) -> bool:        
        if self._hubdata.chargerobject is not None and not self._hubdata.chargerobject.is_initialized:
            return False
        return super().is_initialized

    @property
    def current(self) -> int:
        if self._current is None:
            return 0
        return self._current

    @current.setter
    def current(self, value):
        try:
            self._current = int(value)
        except ValueError:
            pass

    def updatecurrent(self):
        if self._hubdata.chargertype.options.charger_is_outlet is True:
            return
        try:
            self.current = self.get_sensor_from_hass(self._current_attr_name)
        except:
            pass

    async def async_updatecurrent(self):
        if self._hubdata.chargertype.options.charger_is_outlet is True:
            return
        try:
            self.current = await self.async_get_sensor_from_hass(self._current_attr_name)
            return self.current
        except:
           await self.async_log_warning_once()

    HASLOGGED_INITWARN = False
    async def async_log_warning_once(self):
        if not self.HASLOGGED_INITWARN:
            _LOGGER.warning("Chargerobject state was None while getting current. "
                "Updatecurrent will still process but you may see a missmatch in frontend.")
            self.HASLOGGED_INITWARN = True
