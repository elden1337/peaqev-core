from abc import abstractmethod
from ...util import _convert_quarterly_minutes, async_convert_quarterly_minutes
from datetime import datetime
import logging
from ...models.phases import Phases
from ...models.const import (
    CURRENTS_ONEPHASE_1_16,
    CURRENTS_THREEPHASE_1_16,
    CURRENTS_ONEPHASE_1_32,
    CURRENTS_THREEPHASE_1_32,
)

_LOGGER = logging.getLogger(__name__)


ALGORITHM_INPUTS = {
    "stop_caution": [1.075, 0.0032, 0.7],
    "stop": [1.071, 0.00165, 0.8],
    "start_caution": [1.081, 0.0049, 0.4],
    "start": [1.066, 0.0045, 0.5],
}


async def async_calculate_algorithm_inputs(type: str, minute: int) -> float:
    return _calculate_algorithm_inputs(type, minute)


def _calculate_algorithm_inputs(type: str, minute: int) -> float:
    """legacy. remove once peaqhvac is async."""
    inputs = ALGORITHM_INPUTS[type]
    return round((((minute + pow(inputs[0], minute)) * inputs[1]) + inputs[2]) * 100, 2)


class ThresholdBase:
    BASECURRENT = 6

    def __init__(self, hub):
        self._hub = hub
        self._phases = Phases.Unknown
        self._currents = {}

    @property
    def phases(self) -> str:
        return self._phases.name

    @property
    def currents(self) -> dict:
        return self._currents

    # @property
    # @abstractmethod
    # def allowedcurrent(self) -> int:
    #     pass

    def _setcurrentdict(self) -> dict:
        """only allow amps if user has set this value high enough"""
        if self._hub.chargertype.max_amps != 16:
            _threephase = {
                k: v
                for (k, v) in CURRENTS_THREEPHASE_1_32.items()
                if v <= self._hub.chargertype.max_amps
            }
            _onephase = {
                k: v
                for (k, v) in CURRENTS_ONEPHASE_1_32.items()
                if v <= self._hub.chargertype.max_amps
            }
        else:
            _threephase = CURRENTS_THREEPHASE_1_16
            _onephase = CURRENTS_ONEPHASE_1_16
        if hasattr(self._hub.sensors, "carpowersensor"):
            try:
                divid = int(self._hub.sensors.carpowersensor.value) / int(self._hub.sensors.amp_meter.value)
                if int(self._hub.sensors.carpowersensor.value) == 0:
                    self._phases = Phases.Unknown
                    ret = _threephase
                elif divid < 300:
                    self._phases = Phases.OnePhase
                    ret = _onephase
                else:
                    self._phases = Phases.ThreePhase
                    ret = _threephase
            except Exception as e:
                _LOGGER.debug(f"Currents-dictionary: could not divide charger amps with charger power. Falling back to legacy-method. {e}")
                if 0 < int(self._hub.sensors.carpowersensor.value) < 4000:
                    self._phases = Phases.OnePhase
                    ret = _onephase
                else:
                    self._phases = Phases.ThreePhase
                    ret = _threephase
        else:
            self._phases = Phases.ThreePhase
            ret = _threephase
        self._currents = ret
        return ret

    async def async_setcurrentdict(self) -> dict:
        """only allow amps if user has set this value high enough"""
        return self._setcurrentdict()

    @staticmethod
    async def async_stop(
        now_min: int | None = None,
        is_caution_hour: bool = False,
        is_quarterly: bool = False,
    ) -> float:
        _minute = now_min if now_min is not None else datetime.now().minute
        minute = await async_convert_quarterly_minutes(_minute, is_quarterly)
        if is_caution_hour and minute < 45:
            return await async_calculate_algorithm_inputs("stop_caution", minute)
        return await async_calculate_algorithm_inputs("stop", minute)

    @staticmethod
    async def async_start(
        now_min: int | None = None,
        is_caution_hour: bool = False,
        is_quarterly: bool = False,
    ) -> float:
        _minute = now_min if now_min is not None else datetime.now().minute
        minute = await async_convert_quarterly_minutes(_minute, is_quarterly)
        if is_caution_hour and minute < 45:
            return await async_calculate_algorithm_inputs("start_caution", minute)
        return await async_calculate_algorithm_inputs("start", minute)

    @staticmethod
    def base_allowed_current(
        now_min: int,
        now_sec: int,
        moving_avg: float,
        charger_enabled: bool,
        charger_done: bool,
        currents_dict: dict,
        total_energy: float,
        peak: float,
        is_quarterly: bool = False,
        power_canary_amp: int = -1,
    ) -> int:
        minute = _convert_quarterly_minutes(now_min, is_quarterly)
        ret = ThresholdBase.BASECURRENT
        if not charger_enabled or charger_done or moving_avg == 0:
            return ret
        currents = currents_dict
        minsec = minute * 60 + now_sec
        for key, value in currents.items():
            if (
                (((moving_avg + key) / 3600) * (3600 - minsec) + total_energy * 1000)
                / 1000
            ) < peak:
                ret = value
                break
        return min(ret, power_canary_amp) if power_canary_amp > -1 else ret

    @staticmethod
    async def async_base_allowed_current(
        now_min: int,
        now_sec: int,
        moving_avg: float,
        charger_enabled: bool,
        charger_done: bool,
        currents_dict: dict,
        total_energy: float,
        peak: float,
        is_quarterly: bool = False,
        power_canary_amp: int = -1,
    ) -> int:
        minute = await async_convert_quarterly_minutes(now_min, is_quarterly)
        ret = ThresholdBase.BASECURRENT
        if not charger_enabled or charger_done or moving_avg == 0:
            return ret
        currents = currents_dict
        minsec = minute * 60 + now_sec
        for key, value in currents.items():
            if (
                (((moving_avg + key) / 3600) * (3600 - minsec) + total_energy * 1000)
                / 1000
            ) < peak:
                ret = value
                break
        return min(ret, power_canary_amp) if power_canary_amp > -1 else ret

    # legacy below

    @property
    def stop(self) -> float:
        """legacy. remove once peaqhvac is async."""
        is_caution = (
            str(datetime.now().hour) in self._hub.hours.caution_hours
            if self._hub.options.price.price_aware is False
            else False
        )

        return ThresholdBase._stop(
            datetime.now().minute,
            is_caution,
        )

    @property
    def start(self) -> float:
        """legacy. remove once peaqhvac is async."""
        is_caution = (
            str(datetime.now().hour) in self._hub.hours.caution_hours
            if self._hub.options.price.price_aware is False
            else False
        )

        return ThresholdBase._start(
            datetime.now().minute,
            is_caution,
        )

    @staticmethod
    def _stop(now_min: int, is_caution_hour: bool, is_quarterly: bool = False) -> float:
        """legacy. remove once peaqhvac is async."""
        minute = _convert_quarterly_minutes(now_min, is_quarterly)
        if is_caution_hour and minute < 45:
            return _calculate_algorithm_inputs("stop_caution", minute)
        return _calculate_algorithm_inputs("stop", minute)

    @staticmethod
    def _start(
        now_min: int, is_caution_hour: bool, is_quarterly: bool = False
    ) -> float:
        """legacy. remove once peaqhvac is async."""
        minute = _convert_quarterly_minutes(now_min, is_quarterly)
        if is_caution_hour and minute < 45:
            return _calculate_algorithm_inputs("start_caution", minute)
        return _calculate_algorithm_inputs("start", minute)
