from dataclasses import dataclass

@dataclass(frozen=False)
class ChargerOptions:
    powerswitch_controls_charging: bool = False
    charger_is_outlet: bool = False
    ampmeter_is_attribute: bool = False
    powermeter_factor: int = 1
    authentication_required: bool = False