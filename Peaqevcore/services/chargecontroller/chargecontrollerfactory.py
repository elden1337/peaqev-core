from ...hub.hub import HubBase
from .chargecontroller import ChargeController
from .chargecontroller_lite import ChargeControllerLite

class ChargeControllerFactory:
    @staticmethod
    def create(hubbase: HubBase):
        if hubbase.hub.peaqtype_is_lite:
            return ChargeControllerLite(hubbase.hub)
        return ChargeController(hubbase.hub)