from datetime import datetime, date, time
import math
from .schedule_session import ScheduleSession


class Scheduler:
    """This class obj is what constitutes a running scheduler."""
    def __init__(self):
        self.model = ScheduleSession()
        self.active = False

    @property
    def scheduler_active(self) -> bool:
        if self.active is False:
            return False
        return self.model.departuretime > datetime.now() or self.model.remaining_charge > 0

    def create(
        self, 
        desired_charge:float, 
        departuretime:datetime, 
        starttime:datetime=datetime.now(),
        override_settings = False
        ):
        if self.scheduler_active:
            self.cancel()
        self.model.departuretime = departuretime
        self.model.starttime = starttime
        self.model.remaining_charge = desired_charge

    def update(
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
        charge_per_hour = peak - (avg24/1000)
        if charge_per_hour <= 0:
            raise Exception
        
        self.model.remaining_charge -= charged_amount if charged_amount is not None else 0
        self.model.hours_price = [prices, prices_tomorrow]
        cheapest = self._sort_pricelist()
        self.model.hours_charge = self._get_charge_hours(
            cheapest_hours=cheapest, 
            charge_per_hour=charge_per_hour,
            peak=peak
            )

    def cancel(self):
        self.active = False
        self.model.departuretime = datetime.min
        self.model.starttime = datetime.min
        self.model.remaining_charge = 0
    
    def _sort_pricelist(self) -> dict:
        return dict(sorted(self.model.hours_price.items(), key=lambda item: item[1]))
    
    def _get_charge_hours(
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


"""
what to do if i call scheduler at 11AM > 7AM? then the prices for the whole range are not available until 2PM. Should I hold, or charge as per usual (and deduct from remaining charge) if prices are low enough in regular calculation?

"""