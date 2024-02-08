from datetime import datetime
import logging
from ...models.locale.peaks_model import PeaksModel
from ...models.locale.enums.time_periods import TimePeriods
from ..locale.time_pattern import TimePattern

_LOGGER = logging.getLogger(__name__)

class PeaksSelectorService:
    """to be able to handle more than one peak model, for instance with different time periods"""
    def __init__(self, multi_peaks: dict[str, TimePattern] = {}):
        self._multi_peaks: dict[str, TimePattern] = multi_peaks
        self._mock_dt: datetime | None = None
        self._peaks: PeaksModel = PeaksModel({})
        self._all_peaks: dict[str,PeaksModel] = {}
        
    @property
    def dt(self) -> datetime:
        return self._mock_dt if self._mock_dt is not None else datetime.now()

    def set_mock_dt(self, val: datetime | None):
        self._mock_dt = val

    @property
    def peaks(self) -> PeaksModel:
        self._peaks = self.get_active_peaksmodel()
        return self._peaks

    def get_active_peaksmodel(self) -> PeaksModel:
        """get the key which is currently observed"""
        if not len(self._multi_peaks):
            return self._peaks
        # if len(self._all_peaks) == 1:
        #     return list(self._all_peaks.values())[0]
        for k, v in self._multi_peaks.items():
            if v.valid(self.dt):
                #print(f"valid: {k} for {self.dt}")
                if k not in self._all_peaks:
                    self._all_peaks[k] = PeaksModel({})
                return self._all_peaks[k]
        raise Exception("No valid peak model found")
    
