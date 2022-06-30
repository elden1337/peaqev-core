from abc import abstractmethod
from peaqevcore.chargertype_service.models.servicecalls_dto import ServiceCallsDTO, ServiceCallsOptions
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


class ChargerBase:
    def __init__(self):
        self._domainname:str = ""
        self._native_chargerstates:list = []
        self._servicecalls:ServiceCalls = None
        self._chargerstates = CHARGERSTATES_BASE
        #what can we do with these here?
        #self._entityschema = ""
        #self._entities = None
        #self._entityendings = None
        #what can we do with these here?
        self.entities = ChargerEntitiesModel
        self.options = ChargerOptions

    # @property
    # def powermeter_factor(self) -> str:
    #     """
    #     The factor to calculate the power reading. Ie 1 means we get raw watts, 1000 means we get raw kw. 
    #     Converted state is down to factor 1 later which is what is needed for peaq
    #     """
    #     return self.options.powermeter_factor

    # @property
    # def powerswitch_controls_charging(self) -> bool:
    #     return self.options.powerswitch_controls_charging

    @property
    def chargerstates(self) -> dict:
        return self._chargerstates

    # @property
    # def powermeter(self):
    #     return self._powermeter

    # @powermeter.setter
    # def powermeter(self, val):
    #     assert isinstance(val, str)
    #     self._powermeter = val

    # @property
    # def powerswitch(self):
    #     return self._powerswitch

    # @powerswitch.setter
    # def powerswitch(self, val):
    #     assert isinstance(val, str)
    #     self._powerswitch = val

    # @property
    # def chargerentity(self):
    #     return self._chargerentity

    # @chargerentity.setter
    # def chargerentity(self, val):
    #     assert isinstance(val, str)
    #     self._chargerentity = val

    @property
    def servicecalls(self):
        return self._servicecalls

    @property #is this needed?
    def native_chargerstates(self) -> list:
        return self._native_chargerstates

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
