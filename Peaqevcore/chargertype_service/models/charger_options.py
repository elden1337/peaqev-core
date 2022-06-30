@dataclass(frozen=False)
class ChargerOptions:
    powerswitch_controls_charging: bool
    ampmeter_is_attribute: bool
    powermeter_factor: int