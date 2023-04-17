import logging
from .hubmember import HubMember

_LOGGER = logging.getLogger(__name__)


class ChargerObject(HubMember):
    def __init__(self, data_type:list, listenerentity:str, init_override:bool = False):
        self._type = data_type
        self._listenerentity = listenerentity
        self._warned_not_initialized = False
        self._is_initialized = init_override
        super().__init__(data_type=data_type, listenerentity=listenerentity, init_override=init_override)

    @property
    def is_initialized(self) -> bool:
        if self._is_initialized is True:
            return True
        if self.value is not None:
            if str(self.value).lower() in self._type:
                _LOGGER.debug("Chargerobject has initialized")
                self._is_initialized = True
                return True
        # if not self._warned_not_initialized:
        #     _LOGGER.warning(f"Unable to communicate with the charger-integration. Chargerobject value is: {self.value}. Unable to continue. Please check and reboot Home Assistant.")
        #     self._warned_not_initialized = True
        return False

    @HubMember.value.setter
    def value(self, value):
        self._value = value
