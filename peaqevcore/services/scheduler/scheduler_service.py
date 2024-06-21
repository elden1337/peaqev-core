from datetime import datetime, date, time
import math

from .update_scheduler_dto import UpdateSchedulerDTO
from ...models.hourselection.hourselection_options import HourSelectionOptions
from .schedule_session import ScheduleSession
import logging

_LOGGER = logging.getLogger(__name__)


class Scheduler:
    """This class obj is what constitutes a running scheduler."""

    def __init__(self, options: HourSelectionOptions | None = None, test: bool = False):
        self.model = ScheduleSession(hourselection_options=options)
        self.active = False
        self.is_test = test

    @property
    def scheduler_active(self) -> bool:
        if self.active is False:
            return False
        return (
            self.model.departuretime > datetime.now() or self.model.remaining_charge > 0
        )

    async def async_create(
        self,
        desired_charge: float,
        departuretime: datetime,
        starttime: datetime = datetime.now(),
        override_settings=False,
    ):
        if not await self.async_check_parameters(
            desired_charge, departuretime, starttime
        ):
            return
        if self.scheduler_active:
            _LOGGER.debug("Scheduler already active, cancelling")
            await self.async_cancel()
        self.model.departuretime = departuretime
        self.model.starttime = starttime
        self.model.remaining_charge = desired_charge
        self.model.desired_charge = desired_charge
        self.model.override_settings = override_settings

    async def async_check_parameters(
        self, desired_charge: float, departuretime: datetime, starttime: datetime
    ) -> bool:
        if departuretime < starttime:
            _LOGGER.error("Starttime must be before departuretime")
            return False
        if desired_charge <= 0:
            _LOGGER.error("Desired charge for scheduler must be greater than 0")
            return False
        if departuretime <= datetime.now() and self.is_test is False:
            _LOGGER.error(f"Departuretime must be in the future. You added: {departuretime}")
            return False
        return True

    async def async_update(self, dto: UpdateSchedulerDTO, mockdt: datetime | None = None):
        """calculate based on the pricing of hours, current peak and the avg24hr energy consumption"""
        self.model._mock_dt = mockdt if mockdt is not None else datetime.now()
        if self.active and any(
            [
                self.model.remaining_charge <= 0,
                self.model.departuretime <= self.model._mock_dt,
            ]
        ):
            _LOGGER.info("Scheduler is done, remaining charge %s, remaning time %s seconds", self.model.remaining_charge, (self.model.departuretime - self.model._mock_dt).total_seconds())
            return await self.async_cancel()

        self.active = True
        if dto.charge_per_hour < 0:
            _LOGGER.exception("Charge per hour must be greater than 0")
            raise Exception

        self.model.update_remaining_charge(dto.charged_amount)

        self.model.hours_price = [dto.prices, dto.prices_tomorrow]
        cheapest = await self.async_sort_pricelist()
        self.model.hours_charge = await self.async_get_charge_hours(
            cheapest_hours=cheapest, charge_per_hour=dto.charge_per_hour, peak=dto.peak
        )

    async def async_cancel(self):
        self.active = False
        self.model.departuretime = datetime.min
        self.model.starttime = datetime.min
        self.model.remaining_charge = 0

    async def async_sort_pricelist(self) -> dict:
        if (
            self.model.override_settings is False
            and self.model.hourselection_options is not None
        ):
            return await self.async_filter_pricelist()
        return dict(sorted(self.model.hours_price.items(), key=lambda item: item[1]))

    async def async_filter_pricelist(self) -> dict:
        filtered = {
            key: value
            for (key, value) in self.model.hours_price.items()
            if value <= self.model.hourselection_options.absolute_top_price
        }
        ret = dict(sorted(filtered.items(), key=lambda item: item[1]))
        return ret

    async def async_get_charge_hours(
            self,
            cheapest_hours: dict,
            charge_per_hour: float,
            peak: float
    ) -> dict:
        remainder = self.model.remaining_charge
        chargehours:dict = {}
        _LOGGER.debug("calculting charge hours with peak %s and charge per hour %s", peak, charge_per_hour)
        for c in cheapest_hours.keys():
            if remainder <= 0:
                break
            chargehours[c] = 1

            # if remainder > charge_per_hour:
            #     chargehours[c] = 1
            # elif 0 < remainder < charge_per_hour:
            #     chargehours[c] = math.ceil((remainder / peak) * 10) / 10
            #
            if c == datetime.now().replace(minute=0, second=0, microsecond=0):
                fractional = 1-(datetime.now().minute / 60)
                remainder -= fractional * charge_per_hour
            else:
                remainder -= charge_per_hour
        return chargehours
