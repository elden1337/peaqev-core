from dataclasses import dataclass

@dataclass(frozen=False)
class ChargerEntitiesModel:
    chargerentity: str
    ampmeter: str
    powermeter: str
    powerswitch: str