from ...hub.hub_options import HubOptions
from .threshold import Threshold
from .threshold_lite import ThresholdLite

class ThresholdFactory:
    @staticmethod
    def create(options: HubOptions):
        if options.peaqev_lite:
            return ThresholdLite(options)
        return Threshold(options)