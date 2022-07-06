from dataclasses import dataclass, field
from datetime import datetime, time, timedelta, date

MOCKPRICES = [0.142, 0.106, 0.1, 0.133, 0.266, 0.412, 2.113, 3, 4.98, 4.374, 3.913, 3.796, 3.491, 3.241, 3.173, 2.647, 2.288, 2.254, 2.497, 2.247, 2.141, 2.2, 2.113, 0.363]
MOCKPRICES_TOMORROW = [0.063, 0.039, 1.032, 0.034, 0.043, 0.274, 0.539, 1.779, 2.002, 1.75, 1.388, 1.195, 1.162, 0.962, 0.383, 0.387, 0.63, 1.202, 1.554, 1.75, 1.496, 1.146, 0.424, 0.346]


@dataclass
class ScheduleSession:
    remaining_charge: float
    starttime: datetime
    departuretime: datetime
    _hours_price: dict[datetime, float] = field(init=False)
    #hours_charge: dict[datetime, float] = field(init=False)
    hours_charge: list = field(init=False)
    MOCKDT:datetime = None

    @property
    def hours_price(self):
        return self._hours_price

    @hours_price.setter
    def hours_price(self, price:list):
        today_date = datetime.now().date() if self.MOCKDT is None else self.MOCKDT.date()
        price_dict = {}
        for idx, p in enumerate(price[0]):
            price_dict[datetime.combine(today_date, time(idx, 0))] = p

        if price[1] is not None:
            tomorrow_date = today_date + timedelta(days=1)
            for idx, p in enumerate(price[1]):
                price_dict[datetime.combine(tomorrow_date, time(idx, 0))] = p

        self._hours_price = self._filter_price_dict(price_dict, self.starttime, self.departuretime)

    def _filter_price_dict(self, price_dict:dict, starttime:datetime, departuretime:datetime) -> dict:
        return {key:value for (key,value) in price_dict.items() if starttime <= key <= departuretime}

class Scheduler:
    """This class obj is what constitutes a running scheduler."""
    def __init__(
        self, 
        desired_charge:float, 
        departuretime:datetime, 
        starttime:datetime=datetime.now()
        ):
        self.model = ScheduleSession(desired_charge, starttime, departuretime)

    @property
    def scheduler_running(self):
        """use this prop to check whether regular hourselection should be ignored or not"""
        """use this prop to manipulate string on moneysensor"""
        return self.model.departuretime > datetime.now() or self.model.remaining_charge > 0

    def _sort_pricelist(self) -> dict:
        return dict(sorted(self.model.hours_price.items(), key=lambda item: item[1]))

    def update_calulation(
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
        chargehours = self._get_charge_hours(
            cheapest_hours=cheapest, 
            charge_per_hour=charge_per_hour
            )
        self.model.hours_charge = sorted(chargehours)

    def _get_charge_hours(
        self, 
        cheapest_hours:dict, 
        charge_per_hour:float
        ):
        remainder = self.model.remaining_charge
        chargehours = []
        for c in cheapest_hours.keys():
            remainder -= charge_per_hour
            chargehours.append(c)
            if remainder <= 0:
                break
        return chargehours

s = Scheduler(desired_charge=7, departuretime=datetime.combine(date(2022,7,7), time(7, 0)))
s.update_calulation(avg24=800, peak=1.8, prices=MOCKPRICES, prices_tomorrow=MOCKPRICES_TOMORROW)
print(s.model.hours_charge)
s.update_calulation(avg24=700, peak=1.8, charged_amount=1, prices=MOCKPRICES, prices_tomorrow=MOCKPRICES_TOMORROW)
print(s.model.remaining_charge)
print(s.model.hours_charge)

"""
what to do if i call scheduler at 11AM > 7AM? then the prices for the whole range are not available until 2PM. Should I hold, or charge as per usual (and deduct from remaining charge) if prices are low enough in regular calculation?

"""