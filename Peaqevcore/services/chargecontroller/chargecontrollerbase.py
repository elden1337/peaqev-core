import logging
import time
from datetime import datetime
from ...models.chargecontroller_states import ChargeControllerStates
from abc import abstractmethod
from typing import List, Dict

_LOGGER = logging.getLogger(__name__)


class ChargeControllerBase:  
    def __init__(
        self,
        charger_state_translation:Dict[ChargeControllerStates,List[str]],
        non_hours:List[int] = [],
        timeout:int = 300
    ):
        self._charger_state_translation = self._check_charger_states(charger_state_translation)
        self.done_timeout: int = timeout
        self._latest_charger_start: float = time.time()
        self._non_hours = non_hours

    @property
    def _is_timeout(self) -> bool:
        return time.time() - self.latest_charger_start > self._done_timeout

    @property
    def latest_charger_start(self) -> float:
        return self._latestchargerstart

    @latest_charger_start.setter
    def latest_charger_start(self, val):
        self._latestchargerstart = val

    @property
    @abstractmethod
    def status(self) -> str:
        if self._hub.is_initialized is False:
            return "Hub not ready. Check logs!"
        if self._hub.is_initialized is True:
            if self._chargecontroller_initalized is False:
                self._chargecontroller_initalized = True
                _LOGGER.debug("Chargecontroller is initialized and ready to work!")
        if self._hub.options.charger.charger_is_outlet is True:
            ret = self._get_status_outlet()
        else:
            ret = self._get_status()
        if ret == ChargeControllerStates.Error:
            msg = f"Chargecontroller returned faulty state. Charger reported {self._hub.chargerobject.value.lower()} as state."
            _LOGGER.error(msg)
        return ret.name

    @property
    @abstractmethod
    def charger_state(self) -> ChargeControllerStates:
        """
        Check if you are below the starting threshold of charger
        :return: returns enum ChargeControllerStates
        """
        pass

    @property
    @abstractmethod
    def charger_done(self) -> bool:
        """
        
        :return: returns bool
        """
        pass

    @charger_done.setter
    @abstractmethod
    def charger_done(self, val) -> None:
        """
        
        :return: returns None
        """
        pass

    @property
    @abstractmethod
    def charger_enabled(self) -> bool:
        """
        
        :return: returns bool
        """
        pass

    @property
    @abstractmethod
    def free_charge(self) -> bool:
        """
        
        :return: returns bool
        """
        pass

    @abstractmethod
    def _get_status_charging(self) -> ChargeControllerStates:
        """
        
        :return: returns enum ChargeControllerStates
        """
        pass

    @abstractmethod
    def _get_status_connected(self) -> ChargeControllerStates:
        """
        
        :return: returns enum ChargeControllerStates
        """
        pass

    def _get_status_outlet(self):
        ret = ChargeControllerStates.Error
        update_timer = False
        free_charge = self._hub.locale.data.free_charge(self._hub.locale.data)

        if self._hub.charger_enabled.value is False:
            update_timer = True
            ret = ChargeControllerStates.Disabled
        elif self._hub.charger_done.value is True:
            ret = ChargeControllerStates.Done
        elif datetime.now().hour in self._hub.non_hours and free_charge is False and self._hub.timer.is_override is False:
            update_timer = True
            ret = ChargeControllerStates.Stop
        elif self._hub.chargertype.charger.entities.powerswitch == "on" and self._hub.chargertype.charger.entities.powermeter < 1:
            ret = self._get_status_connected()
            update_timer = (ret == ChargeControllerStates.Stop)
        else:
            ret = self._get_status_charging()
            update_timer = True

        if update_timer is True:
            self.update_latestchargerstart()
        return ret

    def _get_status(self):
        ret = ChargeControllerStates.Error
        update_timer = False
        charger_state = self._hub.chargerobject.value.lower()
        free_charge = self._hub.locale.data.free_charge(self._hub.locale.data)

        if self._hub.charger_enabled.value is False:
            update_timer = True
            ret = ChargeControllerStates.Disabled
        elif charger_state in self._hub.chargertype.charger.chargerstates[ChargeControllerStates.Done]:
            self._hub.charger_done.value = True
            ret = ChargeControllerStates.Done
        elif charger_state in self._hub.chargertype.charger.chargerstates[ChargeControllerStates.Idle]:
            update_timer = True
            ret = ChargeControllerStates.Idle
            if self._hub.charger_done.value is True:
                self._hub.charger_done.value = False
        elif charger_state not in self._hub.chargertype.charger.chargerstates[ChargeControllerStates.Idle] and self._hub.charger_done.value is True:
            ret = ChargeControllerStates.Done
        elif datetime.now().hour in self._hub.non_hours and free_charge is False and self._hub.timer.is_override is False:
            update_timer = True
            ret = ChargeControllerStates.Stop
        elif charger_state in self._hub.chargertype.charger.chargerstates[ChargeControllerStates.Connected]:
            ret = self._get_status_connected(charger_state)
            update_timer = (ret == ChargeControllerStates.Stop)
        elif charger_state in self._hub.chargertype.charger.chargerstates[ChargeControllerStates.Charging]:
            ret = self._get_status_charging()
            update_timer = True

        if update_timer is True:
            self.update_latestchargerstart()
        return ret

    def _is_done(self, charger_state) -> bool:
        if len(self._hub.chargertype.charger.chargerstates[ChargeControllerStates.Done]):
            return charger_state in self._hub.chargertype.charger.chargerstates[ChargeControllerStates.Done]
        return time.time() - self.latest_charger_start > self.done_timeout

    def update_latestchargerstart(self):
        self.latest_charger_start = time.time()

    def _below_start_threshold(
            self,
            predicted_energy: float,
            current_peak: float,
            threshold_start: float
    ) -> bool:
        """
        Check if you are below the starting threshold of charger
        :param predicted_energy: predicted energy for this hour in kWh
        :param current_peak: currently set energy peak, in kWh
        :param threshold_start: the allowed peak percentage to start. 0-1
        :return: returns bool
        """
        return (predicted_energy * 1000) < ((current_peak * 1000) * threshold_start)

    def _above_stop_threshold(
            self,
            predicted_energy: float,
            current_peak: float,
            threshold_stop: float
    ) -> bool:
        """
        Check if you are above the stopping threshold of charger
        :param predicted_energy: predicted energy for this hour in kWh
        :param current_peak: currently set energy peak, in kWh
        :param threshold_stop: the limit peak percentage to stop. 0-1
        :return: returns bool
        """
        return (predicted_energy * 1000) > ((current_peak * 1000) * threshold_stop)

    def _check_charger_states(self, input:Dict[ChargeControllerStates,List[str]]) -> Dict[ChargeControllerStates,List[str]]:
        if len(input) == 0:
            raise AssertionError
        return input


    

    
