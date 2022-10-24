from abc import abstractmethod
from dataclasses import dataclass, field
from ...models.chargertype.servicecalls_dto import ServiceCallsDTO
from ...models.chargertype.servicecalls_options import ServiceCallsOptions
from ...models.chargerstates import CHARGERSTATES
from ...models.chargertype.charger_options import ChargerOptions
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

    @abstractmethod
    def validatecharger(self) -> bool:
        pass

    @abstractmethod
    def get_entities(self):
        pass

    @abstractmethod
    def set_sensors(self):
        pass
