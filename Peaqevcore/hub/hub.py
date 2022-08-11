from ..services.hourselection.hourselectionfactory import HourselectionFactory
from ..services.timer.timer import Timer
from ..services.chargecontroller.chargecontrollerfactory import ChargeControllerFactory
from ..services.threshold.thresholdfactory import ThresholdFactory
from ..services.chargecontroller.chargecontrollerbase import ChargeControllerBase
from ..services.hourselection.hoursbase import Hours
from ..services.prediction.prediction import Prediction
from ..services.production.production import ProductionService
from ..services.scheduler.scheduler import Scheduler
from ..services.session.session import SessionPrice
from ..services.threshold.threshold import ThresholdBase
from .hub_sensors import HubSensors
from .hub_options import HubOptions
from dataclasses import dataclass, field


@dataclass
class HubBase:
    options: HubOptions
    sensors: HubSensors
    timer: Timer()
    #scheduler: Scheduler = field(init=False)
    threshold: ThresholdBase = field(init=False)
    prediction: Prediction = field(init=False)
    #chargecontroller: ChargeControllerBase = field(init=False)
    #locale
    #hours: Hours = field(init=False)
    
    def __post_init__(self):
        #self.hours = HourselectionFactory.create(self.hub)
        #self.scheduler = Scheduler(self.hub, self.hours.options)
        self.threshold = ThresholdFactory.create(self.options)
        self.prediction = Prediction(self.options)
        #self.chargecontroller = ChargeControllerFactory.create(self.hub)
        #self.sensors = HubSensors(self.hub)


