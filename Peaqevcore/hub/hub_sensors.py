from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from ..models.hub.hubmember import CarPowerSensor, HubMember, CurrentPeak
from ..models.hub.power import Power


@dataclass
class IHubSensors(ABC):
    charger_enabled: HubMember = field(init=False)
    charger_done: HubMember = field(init=False)
    current_peak: CurrentPeak = field(init=False)
    totalhourlyenergy: HubMember = field(init=False)
    #locale: LocaleData = field(init=False)
    #chargertype: ChargerTypeData = field(init=False)
    #chargerobject: ChargerObject = field(init=False)
    #chargerobject_switch: ChargerSwitch = field(init=False)
    #hass: HomeAssistant = field(init=False)
    #charger: Charger = field(init=False)

    @abstractmethod
    def __post_init__(self):
        pass


@dataclass
class HubSensorsLite(IHubSensors):
   def __post_init__(self):
        pass


@dataclass
class HubSensors(IHubSensors):
    powersensormovingaverage: HubMember = field(init=False)
    powersensormovingaverage24: HubMember = field(init=False)
    carpowersensor: CarPowerSensor = field(init=False)
    power: Power = field(init=False)

    def __post_init__(self):
        pass


class HubSensorsFactory:
    @staticmethod
    def create() -> IHubSensors:
        return HubSensors()
