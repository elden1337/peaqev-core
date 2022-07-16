from datetime import datetime, date, time
import math
from .schedule_session import ScheduleSession

# MOCKPRICES = [0.006, 0.005, 0.006, 0.01, 0.015, 0.02, 2.115, 2.241, 2.278, 2.279, 2.282, 2.276, 2.271, 2.195, 2.122, 2.029, 2.229, 2.267, 2.271, 2.25, 2.148, 0.138, 0.045, 0.035]
# MOCKPRICES_TOMORROW = [0.036, 0.031, 0.031, 0.033, 0.034, 0.032, 0.033, 0.04, 0.042, 0.044, 0.044, 0.041, 0.037, 0.032, 0.021, 0.02, 0.032, 0.037, 0.043, 0.048, 0.267, 0.161, 0.041, 0.031]


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
        self.active = True
        charge_per_hour = peak - avg24/1000
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
        chargehours = {}
        for c in cheapest_hours.keys():
            remainder -= charge_per_hour
            if remainder <= 0:
                break
            if 0 < remainder < charge_per_hour:
                chargehours[c] = math.ceil((remainder/peak)*10)/10
                break
            else:
                chargehours[c] = 1
        return chargehours


# s = Scheduler()
# date_time_str = '22-07-09 10:00'
# date_time_obj = datetime.strptime(date_time_str, '%y-%m-%d %H:%M')
# s.create(desired_charge=9, departuretime=date_time_obj)
# # s.create(desired_charge=7, departuretime=datetime.combine(date(2022,7,9), time(7, 0)))
# #s.update(avg24=800, peak=1.8, prices=MOCKPRICES, prices_tomorrow=None)
# #print(s.model.hours_charge)
# #print(f"nonhours with only today: {s.model.non_hours}")
# s.update(avg24=291, peak=1.49, charged_amount=0, prices=MOCKPRICES, prices_tomorrow=MOCKPRICES_TOMORROW)
# print(s.model.hours_charge)
# print(f"nonhours with tomorrow: {s.model.non_hours}")
# print(f"cautionhours with tomorrow: {s.model.caution_hours}")
#s.cancel()

"""
what to do if i call scheduler at 11AM > 7AM? then the prices for the whole range are not available until 2PM. Should I hold, or charge as per usual (and deduct from remaining charge) if prices are low enough in regular calculation?

"""