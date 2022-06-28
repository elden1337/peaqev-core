import logging

from .models.servicecalls_dto import ServiceCallsDTO

from .calltype import CallType
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


class ServiceCalls:
    def __init__(
            self,
            domain: str,
            model: ServiceCallsDTO,
            allowupdatecurrent: bool = False,
            update_current_on_termination: bool = False
    ):
        self._domain = domain
        self._allowupdatecurrent = allowupdatecurrent
        self._update_current_on_termination = update_current_on_termination
        self._on = model.on
        self._off = model.off
        self._pause = model.pause
        self._resume = model.resume
        self._update_current = model.update_current

    @property
    def allowupdatecurrent(self) -> bool:
        return self._allowupdatecurrent

    @property
    def allow_update_current_on_termination(self) -> bool:
        return self._update_current_on_termination

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def on(self) -> CallType:
        return self._on

    @property
    def off(self) -> CallType:
        return self._off

    @property
    def pause(self) -> CallType:
        return self._pause

    @property
    def resume(self) -> CallType:
        return self._resume

    @property
    def update_current(self) -> CallType:
        return self._update_current

    def get_call(self, call) -> dict:
        ret = {}
        ret[DOMAIN] = self.domain
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
