from abc import abstractmethod
from dataclasses import dataclass, field
from peaqevcore.chargertype_service.models.servicecalls_dto import ServiceCallsDTO
from peaqevcore.chargertype_service.models.servicecalls_options import ServiceCallsOptions
from ..models.chargerstates import CHARGERSTATES
from .models.charger_options import ChargerOptions
from .models.charger_entities_model import ChargerEntitiesModel
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
        self._servicecalls = ServiceCalls(domain, model, options)

    @abstractmethod
    def validatecharger(self):
        pass

    @abstractmethod
    def getentities(self, domain: str = None, endings: list = None):
        pass

    @abstractmethod
    def set_sensors(self):
        pass
