import logging
from statistics import mean
import time
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

MIN_SAMPLES = 2

def dt_from_epoch(epoch: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))

class Gradient:
    def __init__(
        self, max_age: int, max_samples: int, precision: int = 2, ignore: int|None = None, outlier: float|None = None
    ):
        self._init_time = time.time()
        self._samples = []
        self._gradient = 0
        self._max_age = max_age
        self._max_samples = max_samples
        self._latest_update = 0
        self._ignore = ignore
        self._outlier = outlier
        self._precision = precision

    @property
    def trend(self) -> float:
        self.prepare_gradient()
        data = self._samples
        n = len(data)
        if n < 2:
            return 0
        try:
            sum_x = sum([item[0] / 3600 for item in data])
            sum_y = sum([item[1] for item in data])
            sum_xy = sum([item[1]*item[0] / 3600 for item in data])
            sum_x2 = sum([(item[0] / 3600)**2 for item in data])
            slope = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x**2)
            ret =  round(slope, self._precision)
            return ret if self._precision > 0 else int(ret)
        except ZeroDivisionError as e:
            return 0

    @property
    def gradient(self) -> float:
        self.prepare_gradient()
        return round(self._gradient, self._precision)

    @property
    def gradient_raw(self) -> float:
        self.prepare_gradient()
        return self._gradient

    @property
    def samples(self) -> int:
        return len(self._samples)

    @property
    def samples_raw(self) -> list:
        if len(self._samples) == 0:
            return []
        return sorted(self._samples, key=lambda x: x[0], reverse=True)

    @samples_raw.setter
    def samples_raw(self, lst):
        self._samples.extend(lst)
        self.prepare_gradient()

    @property
    def oldest_sample(self) -> str:
        if len(self._samples) > 0:
            return dt_from_epoch(self._samples[0][0])
        return str(datetime.min)

    @property
    def newest_sample(self) -> str:
        if len(self._samples) > 0:
            return dt_from_epoch(self._samples[-1][0])
        return str(datetime.min)
    
    def peak(self, idx=0) -> float:
        if len(self._samples) > 0:
            return self._samples[idx][1]
        return 0
    
    @property
    def is_clean(self) -> bool:
        return all([time.time() - self._init_time > 300, self.samples > 1])

    def prepare_gradient(self) -> None:
        self._inject_interim_values()
        self._remove_from_list()
        self._set_gradient()

    def _set_gradient(self) -> None:
        values = self._samples
        if len(values) == 1:
            self._gradient = 0
        elif len(values) - 1 > 0:
            try:
                x = (values[-1][1] - values[0][1]) / ((time.time() - values[0][0]) / 3600)
                self._gradient = x
            except ZeroDivisionError as e:
                _LOGGER.warning({e})
                self._gradient = 0

    def _inject_interim_values(self) -> None:
        if self._samples:
            last_sample = self._samples[-1]
            if time.time() - last_sample[0] > 60 * 60:
                self._samples.append((int(time.time() - 30 * 60), last_sample[1]))

    def add_reading(self, val: float, t: float = time.time()):
        if self._ignore is None or self._ignore < val:
            if self._outlier is not None and len(self._samples) > 1 and abs(mean([s[1] for s in self._samples]) - val) > self._outlier:
                print("ignoring value", abs(mean([s[1] for s in self._samples]) - val))
                return
            if (int(t), round(val,3)) not in self._samples:
                self._samples.append((int(t), round(val, 3)))
                self._latest_update = time.time()
                self._remove_from_list()
                self.prepare_gradient()

    def _remove_from_list(self):
        """Removes overflowing number of samples and old samples from the list."""
        while len(self._samples) > self._max_samples:
            self._samples.pop(0)
        old_samples = (x for x in self._samples if time.time() - int(x[0]) > self._max_age)
        for i in old_samples:
            if len(self._samples) > MIN_SAMPLES:
                # Always keep two readings to be able to calc trend
                self._samples.remove(i)

    async def async_set_gradient(self):
       self.prepare_gradient()

    async def async_add_reading(self, val: float, t: float = time.time()):
        self.add_reading(val, t)

    async def async_remove_from_list(self):
        self._remove_from_list()

    def predicted_time_at_value(self, target_value: float) -> datetime|None:
        if self._gradient is None or len(self._samples) < 2:
            return None
        current_gradient = self.trend
        if current_gradient == 0 or all([
            target_value < 0,
            self._samples[-1][1] > 0,
            current_gradient > 0
            ]):
            return None
        time_diff = timedelta(hours=(target_value - self._samples[-1][1]) / current_gradient)
        if time_diff < timedelta(0):
            return None
        return datetime.now() + time_diff
        
    def predicted_value_at_time(self, target_time: datetime) -> float|None:
        if self._gradient is None or target_time < datetime.now() or len(self._samples) < 2:
            return None
        current_gradient = self._gradient
        if current_gradient == 0:
            return None
        time_diff = target_time - datetime.now()
        expected_value = self._samples[-1][1] + (current_gradient * time_diff.total_seconds() / 3600)
        return round(expected_value,self._precision)


# tt = Gradient(max_age=3600, max_samples=100, precision=0)
# tt.add_reading(49, 1712169806)
# tt.add_reading(46,1712169866)
# tt.add_reading(24,1712170406)
# tt.add_reading(12,1712170946)
# tt.add_reading(-52,1712171476)
# tt.add_reading(-97,1712172026)
# tt.add_reading(-145,1712172540)
# tt.add_reading(-151,1712172626)
# tt.add_reading(-156,1712172656)
# tt.add_reading(-162,1712172746)
# tt.add_reading(-167,1712172776)
# tt.add_reading(-173,1712172866)
# print(tt.trend)
# print(tt.predicted_time_at_value(-300))
# print(tt.predicted_time_at_value(-500))
# print(tt.predicted_time_at_value(-1000))