import pytest
from ..chargertype_service.chargertype_base import ChargerBase
from ..chargertype_service.servicecalls import ServiceCalls, ServiceCallsDTO, ServiceCallsOptions
from ..chargertype_service.models.calltype import CallType
from ..chargertype_service.const import (
    OFF, ON, PARAMS, PAUSE, RESUME, UPDATECURRENT, DOMAIN
)

MOCKDOMAIN = "peaqchargerbox"

TESTON = CallType("on")
TESTOFF = CallType("off")
TESTPAUSE = CallType("pause")
TESTRESUME = CallType("resume")
TESTUPDATECURRENT = CallType("set_max_limit", {"testparam1": "param1", "testparam2": "param2"})

def test_get_pause_and_resume_from_blank():
    model = ServiceCallsDTO(TESTON, TESTOFF)
    opt = ServiceCallsOptions(allowupdatecurrent=False, update_current_on_termination=True)
    s = ServiceCalls(MOCKDOMAIN, model, opt)
    pause = s.get_call(PAUSE)
    resume = s.get_call(RESUME)

    assert pause["domain"] == resume["domain"] == MOCKDOMAIN
    assert pause["params"] == TESTOFF.params
    assert pause["pause"] == TESTOFF.call
    assert resume["params"] == TESTON.params
    assert resume["resume"] == TESTON.call

def test_call_updatecurrent_invalid():
    model = ServiceCallsDTO(TESTON, TESTOFF, TESTUPDATECURRENT)
    opt = ServiceCallsOptions(allowupdatecurrent=False, update_current_on_termination=True)
    s = ServiceCalls(MOCKDOMAIN, model, opt)
    with pytest.raises(AttributeError):
              s.get_call(UPDATECURRENT)
