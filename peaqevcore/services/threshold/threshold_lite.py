from datetime import datetime
from .thresholdbase import ThresholdBase


class ThresholdLite(ThresholdBase):
    def __init__(self, hub):
        self._hub = hub
        super().__init__(hub)

    @property
    def allowedcurrent(self) -> int:
        amps = self._setcurrentdict()
        ret = 6
        if self._hub.sensors.charger_enabled.value is False or self._hub.sensors.charger_done.value is True:
            return ret
        currents = amps
        for key, value in currents.items():
            if (((key / 60) * (60 - datetime.now().minute) + self._hub.sensors.totalhourlyenergy.value * 1000) / 1000) < self._hub.current_peak_dynamic:
                ret = value
                break
        return ret
    
    async def async_allowed_current(self) -> int:
        amps = await self.async_setcurrentdict()
        ret = 6
        if self._hub.sensors.charger_enabled.value is False or self._hub.sensors.charger_done.value is True:
            return ret
        currents = amps
        for key, value in currents.items():
            if (((key / 60) * (60 - datetime.now().minute) + self._hub.sensors.totalhourlyenergy.value * 1000) / 1000) < self._hub.current_peak_dynamic:
                ret = value
                break
        return ret
