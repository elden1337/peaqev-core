from .hoursbase import Hours

class RegularHours(Hours):
    def __init__(self, non_hours=None, caution_hours=None):
        super().__init__(False, non_hours, caution_hours)

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