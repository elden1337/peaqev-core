from dataclasses import dataclass
from .calltype import CallType


@dataclass
class ServiceCallsDTO:
    on: CallType
    off: CallType
    pause: CallType | None = None
    resume: CallType | None = None
    update_current: CallType | None = None

    def __post_init__(self):
        if self.pause is None:
            self.pause = self.off
        if self.resume is None:
            self.resume = self.on
