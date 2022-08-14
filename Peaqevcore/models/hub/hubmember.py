import logging
from ...util import nametoid

_LOGGER = logging.getLogger(__name__)


class HubMember:
    def __init__(self, data_type, listenerentity = None, initval = None, name = None):
        self._value = initval
        self._type = data_type
        self._listenerentity = listenerentity
        self.name = name
        self.id = nametoid(self.name) if self.name is not None else None
        self.warned_not_initialized = False
        self._is_initialized = False

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
