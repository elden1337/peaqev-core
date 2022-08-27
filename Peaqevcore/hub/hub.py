from ..services.hourselection.hourselectionfactory import HourselectionFactory
from ..services.timer.timer import Timer
#from ..services.chargecontroller.chargecontrollerfactory import ChargeControllerFactory
from ..services.threshold.thresholdfactory import ThresholdFactory
from ..services.chargecontroller.chargecontrollerbase import ChargeControllerBase
from ..services.hourselection.hoursbase import Hours
from ..services.prediction.prediction import Prediction
from ..services.production.production import ProductionService
from ..services.scheduler.scheduler import SchedulerFacade
from ..services.session.session import SessionPrice
from ..services.threshold.threshold import ThresholdBase
from ..services.locale.Locale import LocaleData
from .hub_sensors import HubSensorsFactory
from .hub_options import HubOptions

class Hub:
    def __init__(self, options: HubOptions, domain: str, state_machine, chargerobj, is_test:bool = False):
        self.state_machine = state_machine
        self.domain = domain

        self.options: HubOptions = options
        self.sensors = HubSensorsFactory.create(self.options)
        self.timer: Timer = Timer()
        self.hours: Hours = HourselectionFactory.create(self)
        self.threshold = ThresholdFactory.create(self)
        self.prediction = Prediction(self)
        self.scheduler = SchedulerFacade(hub=self, options=self.hours.options)

        #chargecontroller: ChargeControllerBase = field(init=False)
        if not is_test:
            self.sensors.setup(state_machine=state_machine, options=options, domain=domain, chargerobject=chargerobj)
            self.sensors.init_hub_values()


