import logging
from dataclasses import dataclass, field
from .models.servicecalls_dto import ServiceCallsDTO

from .models.calltype import CallType
from .const import (
    DOMAIN,
    ON,
    OFF,
    RESUME,
    PAUSE,
    PARAMS,
    UPDATECURRENT,
)

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True)
class ServiceCalls:
    domain:str
    model: ServiceCallsDTO
    on: CallType = field(init=False)
    off: CallType = field(init=False)
    pause: CallType = field(init=False)
    resume: CallType = field(init=False)
    update_current: CallType = field(init=False)

    def __post_init__(self):
        self.on = self.model.on
        self.off = self.model.off,
        self.pause = self.model.pause,
        self.resume = self.model.resume,
        self.update_current = self.model.update_current,

    def get_call(self, call) -> dict:
        ret = {DOMAIN: self.domain}
        calltype = self._get_call_type(call)
        ret[call] = calltype.call
        ret["params"] = calltype.params
        if call is UPDATECURRENT:
            ret[PARAMS] = self.update_current.params
        return ret

    def _get_call_type(self, call) -> CallType:
        _callsdict = {
            ON: self.on,
            OFF: self.off,
            PAUSE: self.pause,
            RESUME: self.resume,
            UPDATECURRENT: self.update_current
        }
        return _callsdict.get(call)
