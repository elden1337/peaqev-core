from .hoursbase import Hours

class RegularHours(Hours):
    def __init__(self, hub):
        self.hub = hub
        super().__init__(False, self.hub.options.nonhours, self.hub.options.cautionhours)

    @property
    def non_hours(self):
        return self._non_hours

    @non_hours.setter
    def non_hours(self, val):
        self._non_hours = val

    @property
    def caution_hours(self):
        return self._caution_hours

    @caution_hours.setter
    def caution_hours(self, val):
        self._caution_hours = val

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