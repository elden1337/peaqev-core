from dataclasses import dataclass, field

@dataclass(frozen=False)
class ChargerEntitiesModel:
    chargerentity: str
    ampmeter: str
    powermeter: str
    powerswitch: str

    entityschema: str = ""
    imported_entities:list = field(default_factory=lambda: [])
    imported_entityendings:list = field(default_factory=lambda: [])
    