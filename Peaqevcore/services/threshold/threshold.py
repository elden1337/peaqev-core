from datetime import datetime
from ...hub.hub import HubBase
from ...models.chargerstates import CHARGERSTATES
from .thresholdbase import ThresholdBase


class Threshold(ThresholdBase):
    def __init__(self, hub: HubBase):
        self._hub = hub
        super().__init__(hub)

    @property
    def allowedcurrent(self) -> int:
        amps = self._setcurrentdict()
        if self._hub.chargecontroller.status is not CHARGERSTATES.Start.name:
            return min(amps.values())
        return ThresholdBase.allowed_current(
            datetime.now().minute,
            self._hub.sensors.powersensormovingaverage.value if self._hub.sensors.powersensormovingaverage.value is not None else 0,
            self._hub.sensors.charger_enabled.value,
            self._hub.sensors.charger_done.value,
            amps,
            self._hub.sensors.totalhourlyenergy.value,
            self._hub.sensors.current_peak_dynamic,
            self._hub.locale.data.is_quarterly(self._hub.locale.data)
        )
