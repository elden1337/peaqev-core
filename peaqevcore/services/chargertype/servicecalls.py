from dataclasses import dataclass, field
from ...models.chargertype.servicecalls_dto import ServiceCallsDTO
from ...models.chargertype.servicecalls_options import ServiceCallsOptions
from ...models.chargertype.calltype import CallType
from ...common.enums.calltype_enum import CallTypes
from .const import (
    DOMAIN,
    PARAMS
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
        ret[PARAMS] = calltype.params
        if call is CallTypes.UpdateCurrent:
            if self.options.allowupdatecurrent is True:
                ret[PARAMS] = self.update_current.params
            else:
                raise AttributeError
        return ret

    def _get_call_type(self, call: CallTypes) -> CallType:
        _callsdict = {
            CallTypes.On: self.on,
            CallTypes.Off: self.off,
            CallTypes.Pause: self.pause,
            CallTypes.Resume: self.resume,
            CallTypes.UpdateCurrent: self.update_current
        }
        return _callsdict.get(call)
