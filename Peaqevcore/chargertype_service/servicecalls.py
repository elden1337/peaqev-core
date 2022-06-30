from dataclasses import dataclass, field
from .models.servicecalls_dto import ServiceCallsDTO
from .models.servicecalls_options import ServiceCallsOptions

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


@dataclass
class ServiceCalls:
    domain:str
    model: ServiceCallsDTO
    options: ServiceCallsOptions
    on: CallType = field(init=False)
    off: CallType = field(init=False)
    pause: CallType = field(init=False)
    resume: CallType = field(init=False)
    update_current: CallType = field(init=False)

    def __post_init__(self):
        self.on = self.model.on
        self.off = self.model.off
        self.pause = self.model.pause
        self.resume = self.model.resume
        self.update_current = self.model.update_current

    def get_call(self, call) -> dict:
        ret = {DOMAIN: self.domain}
        calltype = self._get_call_type(call)
        ret[call] = calltype.call
        ret["params"] = calltype.params
        if call is UPDATECURRENT:
            if self.options.allowupdatecurrent is True:
                ret[PARAMS] = self.update_current.params
            else:
                raise AttributeError
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
