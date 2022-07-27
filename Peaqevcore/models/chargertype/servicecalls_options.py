from dataclasses import dataclass

@dataclass
class ServiceCallsOptions:
    allowupdatecurrent: bool
    update_current_on_termination: bool