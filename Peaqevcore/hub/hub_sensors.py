from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from ..models.hub.hubmember import HubMember
from ..models.hub.currentpeak import CurrentPeak
from ..models.hub.carpowersensor import CarPowerSensor
from ..models.hub.chargerobject import ChargerObject
from ..models.hub.chargerswitch import ChargerSwitch
from ..services.locale.Locale import LocaleData
from ..models.hub.power import Power
from .hub_options import HubOptions
from ..util import nametoid
from typing import Any
from ..services.locale.querytypes.const import HOURLY
from ..models.hub.const import CONSUMPTION_TOTAL_NAME, AVERAGECONSUMPTION, AVERAGECONSUMPTION_24H, CHARGERDONE, CHARGERENABLED


@dataclass
class IHubSensors:
    charger_enabled: HubMember = field(init=False)
    charger_done: HubMember = field(init=False)
    current_peak: CurrentPeak = field(init=False)
    totalhourlyenergy: HubMember = field(init=False)
    carpowersensor: CarPowerSensor = field(init=False)
    locale: LocaleData = field(init=False)
    chargerobject: ChargerObject = field(init=False)
    chargerobject_switch: ChargerSwitch = field(init=False)
    state_machine: Any = field(init=False)
    powersensormovingaverage: HubMember = field(init=False)
    powersensormovingaverage24: HubMember = field(init=False)
    power: Power = field(init=False)

    @abstractmethod
    def setup(self):
        pass

    def setup_base(
            self,
            options: HubOptions,
            state_machine,
            domain: str,
            chargerobject
    ):
        self.chargertype = chargerobject
        self.state_machine = state_machine
        resultdict = {}

        self.charger_enabled = HubMember(
            data_type=bool,
            listenerentity=f"binary_sensor.{domain}_{nametoid(CHARGERENABLED)}",
            initval=options.behavior_on_default
        )
        self.charger_done = HubMember(
            data_type=bool,
            listenerentity=f"binary_sensor.{domain}_{nametoid(CHARGERDONE)}",
            initval=False
        )
        self.locale = LocaleData(
            options.locale,
            domain
        )
        self.current_peak = CurrentPeak(
            data_type=float,
            initval=0,
            startpeaks=options.startpeaks,
        )
        if len(self.chargertype.charger.entities.chargerentity) > 0:
            self.chargerobject = ChargerObject(
                data_type=self.chargertype.charger.native_chargerstates,
                listenerentity=self.chargertype.charger.entities.chargerentity
            )
            resultdict[self.chargerobject.entity] = self.chargerobject.is_initialized

            self.carpowersensor = CarPowerSensor(
                data_type=int,
                listenerentity=self.chargertype.charger.entities.powermeter,
                powermeter_factor=self.chargertype.charger.options.powermeter_factor,
                hubdata=self,
                init_override=True
            )
            self.chargerobject_switch = ChargerSwitch(
                hass=state_machine,
                data_type=bool,
                listenerentity=self.chargertype.charger.entities.powerswitch,
                initval=False,
                currentname=self.chargertype.charger.entities.ampmeter,
                ampmeter_is_attribute=self.chargertype.charger.options.ampmeter_is_attribute,
                hubdata=self,
                init_override=True
            )

        else:
            self.chargerobject = ChargerObject(
                data_type=self.chargertype.charger.native_chargerstates,
                listenerentity="no entity",
                init_override=True
            )
            resultdict[self.chargerobject.entity] = True
            
            self.carpowersensor = CarPowerSensor(
                data_type=int,
                listenerentity=self.chargertype.charger.entities.powermeter,
                powermeter_factor=self.chargertype.charger.options.powermeter_factor,
                hubdata=self
            )
            self.chargerobject_switch = ChargerSwitch(
                hass=state_machine,
                data_type=bool,
                listenerentity=self.chargertype.charger.entities.powerswitch,
                initval=False,
                currentname=self.chargertype.charger.entities.ampmeter,
                ampmeter_is_attribute=self.chargertype.charger.options.ampmeter_is_attribute,
                hubdata=self
            )
        self.totalhourlyenergy = HubMember(
            data_type=float,
            listenerentity=f"sensor.{domain}_{nametoid(CONSUMPTION_TOTAL_NAME)}_{HOURLY}",
            initval=0
        )

    def init_hub_values(self):
        """Initialize values from Home Assistant on the set objects"""
        if self.chargerobject is not None:
            self.chargerobject.value = self.state_machine.states.get(self.chargerobject.entity).state if self.state_machine.states.get(
                self.chargerobject.entity) is not None else 0
        self.chargerobject_switch.value = self.state_machine.states.get(
            self.chargerobject_switch.entity).state if self.state_machine.states.get(
            self.chargerobject_switch.entity) is not None else ""
        self.chargerobject_switch.updatecurrent()
        self.carpowersensor.value = self.state_machine.states.get(self.carpowersensor.entity).state if self.state_machine.states.get(
            self.carpowersensor.entity) is not None else 0
        self.totalhourlyenergy.value = self.state_machine.states.get(self.totalhourlyenergy.entity) if self.state_machine.states.get(
            self.totalhourlyenergy.entity) is not None else 0


@dataclass
class HubSensorsLite(IHubSensors):
   def setup(
        self,
        state_machine,
        options: HubOptions,
        domain: str, 
        chargerobject: Any):

        super().setup_base(state_machine=state_machine, options=options, domain=domain, chargerobject=chargerobject)


@dataclass
class HubSensors(IHubSensors):
    def setup(
        self,
        state_machine,
        options: HubOptions,
        domain: str, 
        chargerobject: Any):

        super().setup_base(state_machine=state_machine, options=options, domain=domain, chargerobject=chargerobject)

        self.powersensormovingaverage = HubMember(
            data_type=int,
            listenerentity=f"sensor.{domain}_{nametoid(AVERAGECONSUMPTION)}",
            initval=0
        )
        self.powersensormovingaverage24 = HubMember(
            data_type=int,
            listenerentity=f"sensor.{domain}_{nametoid(AVERAGECONSUMPTION_24H)}",
            initval=0
        )

        self.power = Power(
            configsensor=options.powersensor,
            powersensor_includes_car=options.powersensor_includes_car
        )

class HubSensorsFactory:
    @staticmethod
    def create(options: HubOptions) -> IHubSensors:
        if options.peaqev_lite:
            return HubSensorsLite()
        return HubSensors()



