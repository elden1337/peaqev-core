from abc import abstractmethod
from dataclasses import dataclass, field
from ...models.chargertype.servicecalls_dto import ServiceCallsDTO
from ...models.chargertype.servicecalls_options import ServiceCallsOptions
from ...models.chargerstates import CHARGERSTATES
from ...models.chargertype.charger_options import ChargerOptions
from ...models.chargertype.calltype import CallType
from ...models.chargertype.charger_entities_model import ChargerEntitiesModel
from .servicecalls import ServiceCalls

CHARGERSTATES_BASE = {
    CHARGERSTATES.Idle: [],
    CHARGERSTATES.Connected: [],
    CHARGERSTATES.Charging: [],
    CHARGERSTATES.Done: []
}

@dataclass
class ChargerBase:
    domainname:str = ""
    _max_amps = None
    native_chargerstates:list = field(default_factory=lambda: [])
    servicecalls:ServiceCalls = None
    chargerstates = CHARGERSTATES_BASE
    entities = ChargerEntitiesModel
    options = ChargerOptions

    def _set_servicecalls(
            self,
            domain: str,
            model: ServiceCallsDTO,
            options: ServiceCallsOptions,
    ) -> None:
        self.servicecalls = ServiceCalls(domain, model, options)

    @property
    def max_amps(self) -> int:
        if self._max_amps is None:
            return 16
        return self._max_amps

    @max_amps.setter
    def max_amps(self, val) -> None:
        self._max_amps = val

    @abstractmethod
    def get_allowed_amps(self) -> int:
        pass

    @abstractmethod
    def validatecharger(self) -> bool:
        pass

    @abstractmethod
    def get_entities(self):
        pass

    @abstractmethod
    def set_sensors(self):
        pass

    @property
    @abstractmethod
    def domain_name(self) -> str:
        """declare the domain name as stated in HA"""
        pass

    @property
    @abstractmethod
    def entity_endings(self) -> list:
        """declare a list of strings with sensor-endings to help peaqev find the correct sensor-schema."""
        pass

    @property
    @abstractmethod
    def native_chargerstates(self) -> list:
        """declare a list of the native-charger states available for the type."""
        pass

    @property
    @abstractmethod
    def call_on(self) -> CallType:
        pass

    @property
    @abstractmethod
    def call_off(self) -> CallType:
        pass

    @property
    @abstractmethod
    def call_resume(self) -> CallType:
        pass

    @property
    @abstractmethod
    def call_pause(self) -> CallType:
        pass

    @property
    @abstractmethod
    def call_update_current(self) -> CallType:
        pass

    @property
    @abstractmethod
    def servicecalls_options(self) -> ServiceCallsOptions:
        pass
    