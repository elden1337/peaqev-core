import logging
from datetime import datetime
from .hubmember import HubMember
from .const import CURRENTPEAKSENSOR

_LOGGER = logging.getLogger(__name__)


class CurrentPeak(HubMember):
    def __init__(self, data_type: type, initval, startpeaks:dict):
        self._startpeak = self._set_start_peak(startpeaks)
        self._value = initval
        super().__init__(data_type, initval)

    def _set_start_peak(self, peaks:dict) -> float:
        peak = peaks.get(datetime.now().month)
        if peak is None:
            peak = peaks.get(str(datetime.now().month))
            if peak is None:
                raise ValueError
        return peak

    @HubMember.value.getter
    def value(self): # pylint:disable=invalid-overridden-method
        return max(self._value, float(self._startpeak)) if self._value is not None else float(self._startpeak)

