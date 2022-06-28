import logging
from abc import abstractmethod

from ..models.chargerstates import CHARGERSTATES
from .calltype import CallType

from custom_components.peaqev.peaqservice.chargertypes.servicecalls import ServiceCalls

_LOGGER = logging.getLogger(__name__)


class ChargerBase:
    def __init__(self, hass):
        self._hass = hass
        self._domainname = ""
        self._entityendings = None
        self._chargerEntity = None
        self._powermeter = None
        self._native_chargerstates = []
        self.powermeter_factor = 1
        self._powerswitch = None
        self._powerswitch_controls_charging = True
        self.ampmeter = None
        self.ampmeter_is_attribute = None
        self._servicecalls = None
        self._chargerstates = {
            CHARGERSTATES.Idle: [],
            CHARGERSTATES.Connected: [],
            CHARGERSTATES.Charging: [],
            CHARGERSTATES.Done: []
        }
        self._entityschema = ""
        self._entities = None

    @property
    def powerswitch_controls_charging(self) -> bool:
        return self._powerswitch_controls_charging

    @property
    def chargerstates(self) -> dict:
        return self._chargerstates

    @property
    def powermeter(self):
        return self._powermeter

    @powermeter.setter
    def powermeter(self, val):
        assert isinstance(val, str)
        self._powermeter = val

    @property
    def powerswitch(self):
        return self._powerswitch

    @powerswitch.setter
    def powerswitch(self, val):
        assert isinstance(val, str)
        self._powerswitch = val

    @property
    def chargerentity(self):
        return self._chargerentity

    @chargerentity.setter
    def chargerentity(self, val):
        assert isinstance(val, str)
        self._chargerentity = val

    @property
    def servicecalls(self):
        return self._servicecalls

    @property
    def native_chargerstates(self) -> list:
        return self._native_chargerstates

    def _set_servicecalls(
            self,
            domain: str,
            on_call: CallType,
            off_call: CallType,
            pause_call: CallType = None,
            resume_call: CallType = None,
            allowupdatecurrent: bool = False,
            update_current_call: str = None,
            update_current_params: dict = None,
            update_current_on_termination: bool = False
    ) -> None:
        self._servicecalls = ServiceCalls(
            domain,
            on_call,
            off_call,
            pause_call,
            resume_call,
            allowupdatecurrent,
            update_current_call,
            update_current_params,
            update_current_on_termination
        )

    @abstractmethod
    def validatecharger(self):
        pass

    @abstractmethod
    def getentities(self, domain: str = None, endings: list = None):
        pass

    @abstractmethod
    def set_sensors(self):
        pass
