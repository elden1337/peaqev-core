from abc import abstractmethod
from ...util import _convert_quarterly_minutes
from datetime import datetime
import logging
from enum import Enum
from ...models.phases import Phases
from ...models.const import (
    CURRENTS_ONEPHASE_1_16, CURRENTS_THREEPHASE_1_16
)

_LOGGER = logging.getLogger(__name__)

CURRENT_DICT = {
    Phases.OnePhase: CURRENTS_ONEPHASE_1_16,
    Phases.ThreePhase: CURRENTS_THREEPHASE_1_16,
    Phases.Unknown: CURRENTS_THREEPHASE_1_16
}


class ThresholdBase:
    BASECURRENT = 6
    def __init__(self, hub):
        self._hub = hub
        self._phases = Phases.Unknown

    @property
    def phases(self) -> str:
        return self._phases.name

    @property
    def stop(self) -> float:
        return ThresholdBase._stop(
            datetime.now().minute,
            str(datetime.now().hour) in self._hub.hours.caution_hours if self._hub.options.price.price_aware is False else False,
            self._hub.sensors.locale.data.is_quarterly(self._hub.sensors.locale.data)
        )

    @property
    def start(self) -> float:
        return ThresholdBase._start(
            datetime.now().minute,
            str(datetime.now().hour) in self._hub.hours.caution_hours if self._hub.options.price.price_aware is False else False,
            self._hub.sensors.locale.data.is_quarterly(self._hub.sensors.locale.data)
        )

    @property
    @abstractmethod
    def allowedcurrent(self) -> int:
        pass

    def _setcurrentdict(self) -> dict:
    # this one must be done better. Currently cannot accommodate 1-32A single phase for instance.
        try:
            divid = int(self._hub.sensors.carpowersensor.value)/int(self._hub.sensors.chargerobject_switch.current)
            if int(self._hub.sensors.carpowersensor.value) == 0:
                self._phases = Phases.Unknown
            elif divid < 300:
                self._phases = Phases.OnePhase
            else:
                self._phases = Phases.ThreePhase
        except:
            _LOGGER.debug("Currents-dictionary: could not divide charger amps with charger power. Falling back to legacy-method.")
            if 0 < int(self._hub.sensors.carpowersensor.value) < 4000:
                self._phases = Phases.OnePhase
            else:
                self._phases = Phases.ThreePhase
        return CURRENT_DICT[self._phases]

    @staticmethod
    def _stop(
              now_min: int,
              is_caution_hour: bool,
              is_quarterly: bool=False
              ) -> float:
        minute = _convert_quarterly_minutes(now_min, is_quarterly)
        
        if is_caution_hour and minute < 45:
            ret = (((minute+pow(1.075, minute)) * 0.0032) + 0.7)
        else:
            ret = (((minute + pow(1.071, minute)) * 0.00165) + 0.8)
        return round(ret * 100, 2)

    @staticmethod
    def _start(
               now_min: int,
               is_caution_hour: bool,
               is_quarterly:bool=False
               ) -> float:
        minute = _convert_quarterly_minutes(now_min, is_quarterly)
        if is_caution_hour and minute < 45:
            ret = (((minute+pow(1.081, minute)) * 0.0049) + 0.4)
        else:
            ret = (((minute + pow(1.066, minute)) * 0.0045) + 0.5)
        return round(ret * 100, 2)
    
    @staticmethod
    def allowed_current(
            now_min: int,
            moving_avg: float,
            charger_enabled: bool,
            charger_done: bool,
            currents_dict: dict,
            total_energy: float,
            peak: float,
            is_quarterly:bool=False
            ) -> int:
        minute = _convert_quarterly_minutes(now_min, is_quarterly)
        ret = ThresholdBase.BASECURRENT
        if not charger_enabled or charger_done or moving_avg == 0:
            return ret
        currents = currents_dict
        for key, value in currents.items():
            if ((((moving_avg + key) / 60) * (60 - minute) + total_energy * 1000) / 1000) < peak:
                ret = value
                return ret
        return ret