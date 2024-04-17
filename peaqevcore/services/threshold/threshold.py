from datetime import datetime
from ...models.chargecontroller_states import ChargeControllerStates
from .thresholdbase import ThresholdBase


class Threshold(ThresholdBase):
    def __init__(self, hub):
        self._hub = hub
        super().__init__(hub)

    async def async_allowed_current(self) -> int:
        amps = await self.async_setcurrentdict()
        if (
            self._hub.chargecontroller.status_string
            is not ChargeControllerStates.Start.name
        ):
            return min(amps.values())
        return await ThresholdBase.async_base_allowed_current(
            datetime.now().minute,
            datetime.now().second,
            self._hub.sensors.powersensormovingaverage.value
            if self._hub.sensors.powersensormovingaverage.value is not None
            else 0,
            self._hub.sensors.charger_enabled.value,
            self._hub.sensors.charger_done.value,
            amps,
            self._hub.sensors.totalhourlyenergy.value,
            self._hub.current_peak_dynamic,
            await self._hub.sensors.locale.data.async_is_quarterly(),
            self._hub.power.power_canary.max_current_amp,
        )

    def allowed_current(self) -> int:
        amps = self._setcurrentdict()
        if (
            self._hub.chargecontroller.status_string
            is not ChargeControllerStates.Start.name
        ):
            return min(amps.values())
        return ThresholdBase.base_allowed_current(
            datetime.now().minute,
            datetime.now().second,
            self._hub.sensors.powersensormovingaverage.value
            if self._hub.sensors.powersensormovingaverage.value is not None
            else 0,
            self._hub.sensors.charger_enabled.value,
            self._hub.sensors.charger_done.value,
            amps,
            self._hub.sensors.totalhourlyenergy.value,
            self._hub.current_peak_dynamic,
            self._hub.sensors.locale.data.is_quarterly(),
            self._hub.power.power_canary.max_current_amp,
        )
