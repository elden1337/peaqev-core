from __future__ import annotations
import logging
from typing import Tuple
from ...util import nametoid

_LOGGER = logging.getLogger(__name__)


class HubMember:
    def __init__(
        self, 
        data_type, 
        listenerentity = None, 
        initval = None, 
        name = None, 
        init_override:bool = False,
        hass = None
        ):
        self._value = initval
        self._type = data_type
        self._listenerentity, self._listenerattribute = self._set_listeners(listenerentity)
        self.name = name
        self.id = nametoid(self.name) if self.name is not None else None
        self.hass = hass
        self.warned_not_initialized = False
        self._is_initialized = init_override

    def _set_listeners(self, listenerentity:str|None) -> Tuple[str, str|None]:
        """Sets the listening entity. If it contains a |, the value after that will be considered the listener-attribute."""
        if listenerentity is None:
            return None, None
        try:
            _arr = listenerentity.split('|')
            if len(_arr) == 1:
                return listenerentity, None
            return _arr[0], _arr[1]
        except:
            _LOGGER.debug(f"could not handle this listenerentity in split-setup: {listenerentity}")
            return None, None

    @property
    def is_initialized(self) -> bool:
        if self._is_initialized:
            return True
        if isinstance(self.value, self._type):
            _LOGGER.debug(f"{self._listenerentity} has initialized")
            self._is_initialized = True
            return True
        if not self.warned_not_initialized:
            _LOGGER.error(f"{self._listenerentity} was not {self._type}. {self.value}")
            self.warned_not_initialized = True
        return False

    @property
    def entity(self) -> str:
        return self._listenerentity

    @entity.setter
    def entity(self, val: str):
        self._listenerentity = val

    @property
    def use_attribute(self) -> bool:
        return self._listenerattribute is not None

    @property
    def attribute(self) -> str:
        return self._listenerattribute

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, self._type):
            self._value = value
        elif self._type is float:
            try:
                self._value = float(value)
            except ValueError:
                self._value = 0
        elif self._type is int:
            try:
                self._value = int(float(value))
            except ValueError:
                self._value = 0
        elif self._type is bool:
            try:
                if value is None:
                    self._value = False
                elif value.lower() == "on":
                    self._value = True
                elif value.lower() == "off":
                    self._value = False
            except ValueError as e:
                msg = f"Could not parse bool, setting to false to be sure {value}, {self._listenerentity}, {e}"
                _LOGGER.error(msg)
                self._value = False
        elif  self._type is str:
            self._value = str(value)

    def get_sensor_from_hass(self, sensor:str):
        if self.hass is not None:
            _sensor = sensor.split('|')
            if len(_sensor) == 2:                
                ret = self.hass.states.get(_sensor[0])
                if ret:
                    ret_attr = ret.attributes.get(_sensor[1])
                    return ret_attr
            elif len(_sensor) == 1:
                ret = self.hass.states.get(_sensor[0])
                if ret:
                    return ret
                else:
                    _LOGGER.warning(f"no state found for sensor: {_sensor[0]}")

    async def async_get_sensor_from_hass(self, sensor:str):
        if self.hass is not None:
            _sensor = sensor.split('|')
            if len(_sensor) == 2:                
                ret = self.hass.states.get(_sensor[0])
                if ret:
                    ret_attr = ret.attributes.get(_sensor[1])
                    return ret_attr
            elif len(_sensor) == 1:
                ret = self.hass.states.get(_sensor[0])
                if ret:
                    return ret
                else:
                    _LOGGER.warning(f"no state found for sensor: {_sensor[0]}")
            