from dataclasses import dataclass
from ..calltype import CallType

@dataclass
class ServiceCallsDTO:
    on: CallType
    off: CallType
    pause: CallType = None
    resume: CallType = None
    update_current: CallType = None
    # update_current_call: str = None
    # update_current_params: dict = None




test1 = CallType("hej", {})

model = ServiceCallsDTO(test1, test1, None, None, None, None)

print(model.off_call)