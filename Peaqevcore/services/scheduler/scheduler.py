from datetime import datetime, date, time
import math
from ...models.hourselection.hourselectionmodels import HourSelectionOptions
from .schedule_session import ScheduleSession
from ...models.chargecontroller_states import ChargeControllerStates

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

    def create(
        self, 
        desired_charge:float, 
        departuretime:datetime, 
        starttime:datetime=datetime.now(),
        override_settings = False
        ):
        if self.scheduler_active:
            self._cancel()
        self.model.departuretime = departuretime
        self.model.starttime = starttime
        self.model.remaining_charge = desired_charge
        self.model._override_settings = override_settings

    def _update(
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
            return self._cancel()
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

    def _cancel(self):
        self.active = False
        self.model.departuretime = datetime.min
        self.model.starttime = datetime.min
        self.model.remaining_charge = 0
    
    def _sort_pricelist(self) -> dict:
        if self.model._override_settings is False and self.model.hourselection_options is not None:
            return self._filter_pricelist()    
        return dict(sorted(self.model.hours_price.items(), key=lambda item: item[1]))
    
    def _filter_pricelist(self) -> dict:
        filtered = {key:value for (key,value) in self.model.hours_price.items() if value <= self.model.hourselection_options.absolute_top_price}
        ret= dict(sorted(filtered.items(), key=lambda item: item[1]))
        return ret

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


class SchedulerFacade(Scheduler):
    def __init__(self, hub, options):
        self._hub = hub
        super().__init__(options)
        self.schedule_created = False

    def create_schedule(self, charge_amount: float, departure_time: datetime, schedule_starttime: datetime, override_settings: bool = False):
        if not self.scheduler_active:
            self.create(charge_amount, departure_time, schedule_starttime, override_settings)
        self.schedule_created = True

    def update(self):
        self._update(
            avg24=self._hub.sensors.powersensormovingaverage24.value,
            peak=self._hub.current_peak_dynamic,
            charged_amount=self._hub.charger.session.session_energy,
            prices=self._hub.hours.prices,
            prices_tomorrow=self._hub.hours.prices_tomorrow
        )
        self.check_states()

    def cancel(self):
        self._cancel()
        self.schedule_created = False

    def check_states(self):
        if not self.scheduler_active and self.schedule_created:
            self.cancel()
        elif self._hub.chargecontroller.status is ChargeControllerStates.Done.name:
            self.cancel()

    @property
    def non_hours(self) -> list:
        return self.model.non_hours

    @property
    def caution_hours(self) -> dict:
        """dynamic caution hours"""
        return self.model.caution_hours
