from datetime import datetime
from ...models.chargecontroller_states import ChargeControllerStates
from .scheduler import Scheduler


class SchedulerFacade(Scheduler):
    def __init__(self, hub, options):
        self.hub = hub
        super().__init__(options)
        self.schedule_created = False

    async def async_create_schedule(
        self,
        charge_amount: float,
        departure_time: datetime,
        schedule_starttime: datetime,
        override_settings: bool = False,
    ):
        if not self.scheduler_active:
            await self.async_create(
                charge_amount, departure_time, schedule_starttime, override_settings
            )
        self.schedule_created = True

    async def async_update_facade(self):
        await self.async_update(
            self.hub.sensors.powersensormovingaverage24.value,
            self.hub.current_peak_dynamic,
            self.hub.chargecontroller.session.session_energy,
            self.hub.hours.prices,
            self.hub.hours.prices_tomorrow,
        )
        await self.async_check_states()

    async def async_cancel_facade(self):
        await self.async_cancel()
        self.schedule_created = False

    async def async_check_states(self):
        if not self.scheduler_active and self.schedule_created:
            await self.async_cancel_facade()
        elif (
            self.hub.chargecontroller.status_string is ChargeControllerStates.Done.name
        ):
            await self.async_cancel_facade()

    @property
    def non_hours(self) -> list:
        return self.model.non_hours

    @property
    def caution_hours(self) -> dict:
        """dynamic caution hours"""
        return self.model.caution_hours
