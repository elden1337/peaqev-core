# import logging
# from .hubmember import HubMember

# _LOGGER = logging.getLogger(__name__)


# class ChargerObject(HubMember):
#     def __init__(
#         self, data_type: list, listenerentity: str, init_override: bool = False
#     ):
#         self._native_values = data_type
#         self._type = str
#         # self._listenerentity = listenerentity
#         self._warned_not_initialized = False
#         self._is_initialized = init_override
#         super().__init__(
#             data_type=self._type,
#             listenerentity=listenerentity,
#             init_override=init_override,
#         )

#     @property
#     def is_initialized(self) -> bool:
#         if self._is_initialized is True:
#             return True
#         if self.value is not None:
#             if str(self.value).lower() in self._native_values:
#                 _LOGGER.debug("Chargerobject has initialized")
#                 self._is_initialized = True
#                 return True
#         # if not self._warned_not_initialized:
#         #     _LOGGER.warning(f"Unable to communicate with the charger-integration. Chargerobject value is: {self.value}. Unable to continue. Please check and reboot Home Assistant.")
#         #     self._warned_not_initialized = True
#         return False

#     @HubMember.value.setter
#     def value(self, value):
#         self._value = value


import logging
from .hubmember import HubMember

_LOGGER = logging.getLogger(__name__)


class ChargerObject(HubMember):
    def __init__(
        self, data_type: list, listenerentity: str, init_override: bool = False
    ):
        self._native_states = data_type
        self._type = type(data_type[0])
        self._listenerentity = listenerentity
        self._warned_not_initialized = False
        self._is_initialized = init_override
        super().__init__(
            data_type=self._type,
            listenerentity=listenerentity,
            init_override=init_override,
        )

    @property
    def is_initialized(self) -> bool:
        if self._is_initialized is True:
            return True
        if self.value is not None:
            if str(self.value).lower() in self._native_states:
                _LOGGER.debug("Chargerobject has initialized")
                self._is_initialized = True
                return True
        return False

    @HubMember.value.getter
    def value(self):
        self.update()
        _LOGGER.info(f"Chargerobject value is: {self._value}")
        return self._value
