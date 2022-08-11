from .hoursbase import Hours

class RegularHours(Hours):
    def __init__(self, hub: any):
        self.hub = hub
        super().__init__(False, self.hub.non_hours, self.hub.caution_hours)

    @property
    def nordpool_entity(self):
        pass

    def update_nordpool(self):
        pass

    @property
    def dynamic_caution_hours(self) -> dict:
        pass

    @property
    def is_initialized(self) -> bool:
        return True

    @property
    def options(self):
        pass