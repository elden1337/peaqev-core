from datetime import datetime
import math
from .schedule_session import ScheduleSession

# MOCKPRICES = [0.142, 0.106, 0.1, 0.133, 0.266, 0.412, 2.113, 3, 4.98, 4.374, 3.913, 3.796, 3.491, 3.241, 3.173, 2.647, 2.288, 2.254, 2.497, 2.247, 2.141, 2.2, 2.113, 0.363]
# MOCKPRICES_TOMORROW = [0.063, 0.039, 1.032, 0.034, 0.043, 0.274, 0.539, 1.779, 2.002, 1.75, 1.388, 1.195, 1.162, 0.962, 0.383, 0.387, 0.63, 1.202, 1.554, 1.75, 1.496, 1.146, 0.424, 0.346]


class Scheduler:
    """This class obj is what constitutes a running scheduler."""
    def __init__(self):
        self.model = ScheduleSession()

    @property
    def scheduler_active(self):
        """use this prop to check whether regular hourselection should be ignored or not"""
        """use this prop to manipulate string on moneysensor"""
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

        #todo: parse and validate the datetime-objects.
        self.model.departuretime = departuretime
        self.model.starttime = starttime
        self.model.remaining_charge = desired_charge

    def update(
        self,
        avg24:float,
        peak:float,
        charged_amount:float = None, #charged amount since last call, if any
        prices:list = None,
        prices_tomorrow:list = None,
        mockdt:datetime = datetime.now()
        ):
        """calculate based on the pricing of hours, current peak and the avg24hr energy consumption"""
        charge_per_hour = peak - avg24/1000
        if charge_per_hour <= 0:
            raise Exception
        
        self.model.remaining_charge -= charged_amount if charged_amount is not None else 0
        self.model.hours_price = [prices, prices_tomorrow]
        cheapest = self._sort_pricelist()

        #todo: make it possible to set caution-hours if needed.
        self.model.hours_charge = self._get_charge_hours(
            cheapest_hours=cheapest, 
            charge_per_hour=charge_per_hour,
            peak=peak
            )

    def cancel(self):
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
# s.create(desired_charge=7, departuretime=datetime.combine(date(2022,7,8), time(7, 0)))
# s.update(avg24=800, peak=1.8, prices=MOCKPRICES, prices_tomorrow=None)
# print(s.model.hours_charge)
# #print(f"nonhours with only today: {s.model.non_hours}")
# s.update(avg24=900, peak=1.8, charged_amount=0, prices=MOCKPRICES, prices_tomorrow=MOCKPRICES_TOMORROW)
# print(s.model.hours_charge)
# print(f"nonhours with tomorrow: {s.model.non_hours}")
# print(f"cautionhours with tomorrow: {s.model.caution_hours}")

# s.cancel()

"""
what to do if i call scheduler at 11AM > 7AM? then the prices for the whole range are not available until 2PM. Should I hold, or charge as per usual (and deduct from remaining charge) if prices are low enough in regular calculation?

"""