from datetime import datetime
from ...models.chargecontroller_states import ChargeControllerStates
from .scheduler import Scheduler


class SchedulerFacade(Scheduler):
    def __init__(self, hub, options):
        self._hub = hub
        super().__init__(options)
        self.schedule_created = False

    # def create_schedule(self, charge_amount: float, departure_time: datetime, schedule_starttime: datetime, override_settings: bool = False):
    #     if not self.scheduler_active:
    #         self.create(charge_amount, departure_time, schedule_starttime, override_settings)
    #     self.schedule_created = True

    async def async_create_schedule(self, charge_amount: float, departure_time: datetime, schedule_starttime: datetime, override_settings: bool = False):
        if not self.scheduler_active:
            await self.async_create(charge_amount, departure_time, schedule_starttime, override_settings)
        self.schedule_created = True

    # def update(self):
    #     self._update(
    #         avg24=self._hub.sensors.powersensormovingaverage24.value, #todo: refactor
    #         peak=self._hub.current_peak_dynamic, #todo: refactor
    #         charged_amount=self._hub.chargecontroller.charger.session.session_energy, #todo: refactor
    #         prices=self._hub.hours.prices, #todo: refactor
    #         prices_tomorrow=self._hub.hours.prices_tomorrow #todo: refactor
    #     )
    #     self.check_states()

    async def async_update_facade(self):
        await self.async_update(self._hub.sensors.powersensormovingaverage24.value,
                                self._hub.current_peak_dynamic,
                                self._hub.chargecontroller.charger.session.session_energy,
                                self._hub.hours.prices,
                                self._hub.hours.prices_tomorrow)
        await self.async_check_states()

    # def cancel(self):
    #     self._cancel()
    #     self.schedule_created = False

    async def async_cancel_facade(self):
        await self.async_cancel()
        self.schedule_created = False

    async def async_check_states(self):
        if not self.scheduler_active and self.schedule_created:
            await self.async_cancel_facade()
        elif self._hub.chargecontroller.status_string is ChargeControllerStates.Done.name:
            await self.async_cancel_facade()

    # def check_states(self):
    #     if not self.scheduler_active and self.schedule_created:
    #         self.cancel()
    #     elif self._hub.chargecontroller.status_string is ChargeControllerStates.Done.name:
    #         self.cancel()

    @property
    def non_hours(self) -> list:
        return self.model.non_hours

    @property
    def caution_hours(self) -> dict:
        """dynamic caution hours"""
        return self.model.caution_hours