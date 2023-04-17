from dataclasses import dataclass, field

@dataclass(frozen=False)
class ChargerEntitiesModel:
    powermeter: str
    powerswitch: str
    ampmeter: str = ""
    maxamps: str = ""
    chargerentity: str = ""
    entityschema: str = ""
    imported_entities:list = field(default_factory=lambda: [])
    imported_entityendings:list = field(default_factory=lambda: [])