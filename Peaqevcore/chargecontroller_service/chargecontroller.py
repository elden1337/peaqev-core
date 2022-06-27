import time
from datetime import datetime
from ..models.chargerstates import CHARGERSTATES
from abc import abstractmethod


class ChargeControllerBase:  
    def __init__(
        self,
        #init types from core
        #charger_states:list[CHARGERSTATES],
        #init types from core
        charger_state_translation:dict[CHARGERSTATES,list[str]],
        non_hours:list[int] = [],
        timeout:int = 180
    ):
        self._charger_state_translation = self._check_charger_states(charger_state_translation)
        self._done_timeout: int = timeout
        self._latest_charger_start: float = time.time()
        self._non_hours = non_hours
        #self._charger_states = charger_states
    
    @property
    def done_timeout(self):
        return self._done_timeout

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
        """
        
        :return: returns string of enum CHARGERSTATES
        """
        pass
        # if self._hub.is_initialized is False:
        #     return "Hub not ready. Check logs!"
        # if self._hub.is_initialized is True:
        #     if self._chargecontroller_initalized is False:
        #         self._chargecontroller_initalized = True
        #         #_LOGGER.debug("Chargecontroller is initialized and ready to work!")
        # if self._hub.charger_enabled.value is False:
        #     return CHARGERSTATES.Disabled.name
        # ret = self._get_status()
        # if ret == CHARGERSTATES.Error:
        #     pass
        #     #msg = f"Chargecontroller returned faulty state. Charger reported {self._hub.chargerobject.value.lower()} as state."
        #     #_LOGGER.error(msg)
        # return ret.name

    @property
    @abstractmethod
    def charger_state(self) -> CHARGERSTATES:
        """
        Check if you are below the starting threshold of charger
        :return: returns enum CHARGERSTATES
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
    def _get_status_charging(self) -> CHARGERSTATES:
        """
        
        :return: returns enum CHARGERSTATES
        """
        pass

    @abstractmethod
    def _get_status_connected(self) -> CHARGERSTATES:
        """
        
        :return: returns enum CHARGERSTATES
        """
        pass


    def _get_status(self):
        ret = CHARGERSTATES.Error
        update_timer = False
        
        if self.charger_state in self._charger_states[CHARGERSTATES.Done]:
            self.charger_done = True
            ret = CHARGERSTATES.Done
        elif self.charger_state in self._charger_states[CHARGERSTATES.Idle]:
            update_timer = True
            ret = CHARGERSTATES.Idle
            if self.charger_done is True:
                self.charger_done = False
        elif self.charger_state in self._charger_states[CHARGERSTATES.Connected] and self.charger_enabled is False:
            update_timer = True
            ret = CHARGERSTATES.Connected
        elif self.charger_state not in self._charger_states[CHARGERSTATES.Idle] and self.charger_done is True:
            ret = CHARGERSTATES.Done
        elif datetime.now().hour in self._non_hours and self.free_charge is False:
            update_timer = True
            ret = CHARGERSTATES.Stop
        elif self.charger_state in self._charger_states[CHARGERSTATES.Connected]:
            ret = self._get_status_connected()
            update_timer = (ret == CHARGERSTATES.Stop)
        elif self.charger_state in self._charger_states[CHARGERSTATES.Charging]:
            ret = self._get_status_charging()
            update_timer = True

        if update_timer is True:
            self.update_latestchargerstart()
        return ret

    def update_latestchargerstart(self):
        self.latest_charger_start = time.time()

    def below_start_threshold(
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

    def above_stop_threshold(
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

    def _check_charger_states(self, input:dict[CHARGERSTATES,list[str]]) -> dict[CHARGERSTATES,list[str]]:
        if len(input) == 0:
            raise AssertionError
        for i in input:
            if len(input[i]) == 0:
                raise AssertionError
        return input


    

    
