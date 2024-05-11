from datetime import datetime

from ..hoursselection_service_new.models.hour_price import HourPrice
from ..hoursselection_service_new.models.permittance_type import PermittanceType
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

    def combine_future_hours(self, future_hours: list[HourPrice]):
        if not self.active:
            return future_hours

        dep = self.model.departuretime
        start = self.model.starttime

        hours_charge = self.model.hours_charge

        for hour_price in future_hours:
            if start <= hour_price.dt < dep:
                hour_price.permittance_type = PermittanceType.Scheduler
                if hour_price.dt in hours_charge:
                    hour_price.permittance = hours_charge[hour_price.dt]
                else:
                    hour_price.permittance = 0
        return future_hours

    #todo: redo these to work as future-hours instead. preferably reuse logic from hourselectionservice
    @property
    def non_hours(self) -> list:
        return self.model.non_hours

    @property
    def caution_hours(self) -> dict:
        """dynamic caution hours"""
        return self.model.caution_hours
