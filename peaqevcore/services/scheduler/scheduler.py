from datetime import datetime, date, time
import math
from ...models.hourselection.hourselection_options import HourSelectionOptions
from .schedule_session import ScheduleSession


class Scheduler:
    """This class obj is what constitutes a running scheduler."""
    def __init__(self, options:HourSelectionOptions = None):
        self.model = ScheduleSession(hourselection_options=options)
        self.active = False

    @property
    def scheduler_active(self) -> bool:
        if self.active is False:
            return False
        return self.model.departuretime > datetime.now() or self.model.remaining_charge > 0

    async def async_create(self, desired_charge:float, departuretime:datetime, starttime:datetime=datetime.now(), override_settings = False):
        if self.scheduler_active:
            await self.async_cancel()
        self.model.departuretime = departuretime
        self.model.starttime = starttime
        self.model.remaining_charge = desired_charge
        self.model._override_settings = override_settings

    async def async_update(
        self,
        avg24:float,
        peak:float,
        charged_amount:float = None,
        prices:list = None,
        prices_tomorrow:list = None,
        mockdt:datetime = datetime.now()
        ):
        """calculate based on the pricing of hours, current peak and the avg24hr energy consumption"""
        self.model.MOCKDT = mockdt
        self.active = True
        if self.model.remaining_charge <= 0 or self.model.departuretime <= mockdt:
            return await self.async_cancel()
        charge_per_hour = peak - (avg24/1000)
        if charge_per_hour <= 0:
            raise Exception
        
        self.model.remaining_charge -= charged_amount if charged_amount is not None else 0
        self.model.hours_price = [prices, prices_tomorrow]
        cheapest = await self.async_sort_pricelist()
        self.model.hours_charge = await self.async_get_charge_hours(
            cheapest_hours=cheapest, 
            charge_per_hour=charge_per_hour,
            peak=peak
            )

    async def async_cancel(self):
        self.active = False
        self.model.departuretime = datetime.min
        self.model.starttime = datetime.min
        self.model.remaining_charge = 0
    
    async def async_sort_pricelist(self) -> dict:
        if self.model._override_settings is False and self.model.hourselection_options is not None:
            return await self.async_filter_pricelist()    
        return dict(sorted(self.model.hours_price.items(), key=lambda item: item[1]))
    
    async def async_filter_pricelist(self) -> dict:
        filtered = {key:value for (key,value) in self.model.hours_price.items() if value <= self.model.hourselection_options.absolute_top_price}
        ret= dict(sorted(filtered.items(), key=lambda item: item[1]))
        return ret

    async def async_get_charge_hours(
        self, 
        cheapest_hours:dict, 
        charge_per_hour:float,
        peak:float
        ) -> dict:
        remainder = self.model.remaining_charge
        chargehours = dict()
        for c in cheapest_hours.keys():
            if remainder <= 0:
                break
            if remainder > charge_per_hour:
                chargehours[c] = 1
            elif 0 < remainder < charge_per_hour:
                chargehours[c] = math.ceil((remainder/peak)*10)/10
            remainder -= charge_per_hour
        return chargehours
