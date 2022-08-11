from dataclasses import dataclass, field
from ..models.hub.hubmember import HubMember, CurrentPeak
from ..models.hub.power import Power


@dataclass
class HubSensors:
    charger_enabled: HubMember
    charger_done: HubMember
    
    powersensormovingaverage: HubMember
    powersensormovingaverage24: HubMember
    totalhourlyenergy: HubMember
    power: Power
    current_peak: CurrentPeak

    #locale: LocaleData
    #chargertype: ChargerTypeData
    #carpowersensor: CarPowerSensor
    #chargerobject: HubMember
    #chargerobject_switch: ChargerSwitch
    #hass: HomeAssistant
    #charger: Charger


    def __post_init__(self):
    #     charger_enabled = HubMember(
    #         data_type=bool,
    #         listenerentity=f"binary_sensor.{domain}_{ex.nametoid(CHARGERENABLED)}",
    #         initval=config_inputs["behavior_on_default"]
    #     )
    # charger_done = HubMember(
    #         data_type=bool,
    #         listenerentity=f"binary_sensor.{domain}_{ex.nametoid(CHARGERDONE)}",
    #         initval=False
    #     )
        pass