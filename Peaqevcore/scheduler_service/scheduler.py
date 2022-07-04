from dataclasses import dataclass, field
from datetime import datetime, time, timedelta, date

MOCKPRICES = [0.142, 0.106, 0.1, 0.133, 0.266, 0.412, 2.113, 3, 4.98, 4.374, 3.913, 3.796, 3.491, 3.241, 3.173, 2.647, 2.288, 2.254, 2.497, 2.247, 2.141, 2.2, 2.113, 0.363]
MOCKPRICES_TOMORROW = [0.063, 0.039, 0.032, 0.034, 0.043, 0.274, 0.539, 1.779, 2.002, 1.75, 1.388, 1.195, 1.162, 0.962, 0.383, 0.387, 0.63, 1.202, 1.554, 1.75, 1.496, 1.146, 0.424, 0.346]


@dataclass
class ScheduleSession:
    remaining_charge: float
    starttime: datetime
    departuretime: datetime
    hours_price: dict[datetime, float] = field(init=False)
    #hours_charge: dict[datetime, float] = field(init=False)
    hours_charge: list = field(init=False)


class Scheduler:
    MOCKDT:datetime = None

    """This class obj is what constitutes a running scheduler."""
    def __init__(
        self, 
        desired_charge:float, 
        departuretime:datetime, 
        starttime:datetime=datetime.now()
        ):
        self._model = ScheduleSession(desired_charge, starttime, departuretime)
        self._model.hours_price = self.get_price_dict(MOCKPRICES, MOCKPRICES_TOMORROW)

    def get_price_dict(self, prices:list, prices_tomorrow:list = None) -> dict:
        today_date = datetime.now().date() if self.MOCKDT is None else self.MOCKDT.date()
        price_dict = {}
        for idx, p in enumerate(prices):
            price_dict[datetime.combine(today_date, time(idx, 0))] = p

        if prices_tomorrow is not None:
            tomorrow_date = today_date + timedelta(days=1)
            for idx, p in enumerate(prices_tomorrow):
                price_dict[datetime.combine(tomorrow_date, time(idx, 0))] = p

        return self._filter_price_dict(price_dict, self._model.starttime, self._model.departuretime)

    def _filter_price_dict(self, price_dict:dict, starttime:datetime, departuretime:datetime) -> dict:
        return {key:value for (key,value) in price_dict.items() if starttime <= key <= departuretime}

    def _sort_pricelist(self) -> dict:
        return dict(sorted(self._model.hours_price.items(), key=lambda item: item[1]))

    def update_calulation(
        self,
        avg24:float,
        peak:float
        ):
        """calculate based on the pricing of hours, current peak and the avg24hr energy consumption"""
        charge_per_hour = peak - avg24/1000
        if charge_per_hour <= 0:
            raise Exception
        cheapest = self._sort_pricelist()

        remaining = self._model.remaining_charge
        chargehours = list()
        for c in cheapest.keys():
            remaining -= charge_per_hour
            chargehours.append(c)
            if remaining <= 0:
                break
        print(f"remaining estimated: {remaining}")
        self._model.hours_charge = sorted(chargehours)


s = Scheduler(7, datetime.combine(date(2022,7,5), time(7, 0)))
#print(s._model.hours_price)
s.update_calulation(avg24=800, peak=1.8)
print(s._model.hours_charge)

"""
what to do if i call scheduler at 11AM > 7AM? then the prices for the whole range are not available until 2PM. Should I hold, or charge as per usual (and deduct from remaining charge) if prices are low enough in regular calculation?

"""