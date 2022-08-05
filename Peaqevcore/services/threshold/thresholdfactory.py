from ...hub.hub import HubBase
from .threshold import Threshold
from .threshold_lite import ThresholdLite

class ThresholdFactory:
    @staticmethod
    def create(hubbase: HubBase):
        if hubbase.hub.peaqtype_is_lite:
            return ThresholdLite(hubbase.hub)
        return Threshold(hubbase.hub)