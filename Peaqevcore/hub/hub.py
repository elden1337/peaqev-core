from ..services.timer.timer import Timer
from ..services.chargecontroller.chargecontrollerfactory import ChargeControllerFactory
from ..services.threshold.thresholdfactory import ThresholdFactory
from ..services.chargecontroller.chargecontrollerbase import ChargeControllerBase
from ..services.hourselection.hoursselection import Hoursselectionbase
from ..services.prediction.prediction import Prediction
from ..services.production.production import ProductionService
from ..services.scheduler.scheduler import Scheduler
from ..services.session.session import SessionPrice
from ..services.threshold.threshold import ThresholdBase
from dataclasses import dataclass, field

@dataclass
class HubBase:
    hub: any
    timer: Timer()
    threshold: ThresholdBase = field(init=False)
    prediction: Prediction = field(init=False)
    chargecontroller: ChargeControllerBase = field(init=False)
    #locale
    hours: Hoursselectionbase = field(init=False)
    

    def __post_init__(self):
        self.threshold = ThresholdFactory.create(self.hub)
        self.prediction = Prediction(self.hub)
        self.chargecontroller = ChargeControllerFactory.create(self.hub)
        self.hours = HourSelectionFactory.create(self.hub)




class hub(HubBase):
    def __init__(self):
        self.peaqtype_is_lite = False
        super().__init__(self)

hhub = hub()
print(hhub.threshold.allowed_current)