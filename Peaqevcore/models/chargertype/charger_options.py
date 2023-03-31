from dataclasses import dataclass

@dataclass(frozen=False)
class ChargerOptions:
    powerswitch_controls_charging: bool = False #todo: rename this member to something else. It currently conflicts with the servicecall-option named the same (but with different outcome)
    charger_is_outlet: bool = False
    powermeter_factor: int = 1
    authentication_required: bool = False