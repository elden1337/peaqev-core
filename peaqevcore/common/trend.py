import logging
import time
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

MIN_SAMPLES = 2

def dt_from_epoch(epoch: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))

class Gradient:
    def __init__(
        self, max_age: int, max_samples: int, precision: int = 2, ignore: int|None = None
    ):
        self._init_time = time.time()
        self._samples = []
        self._gradient = 0
        self._max_age = max_age
        self._max_samples = max_samples
        self._latest_update = 0
        self._ignore = ignore
        self._precision = precision

    @property
    def gradient(self) -> float:
        self.set_gradient()
        return round(self._gradient, self._precision)

    @property
    def gradient_raw(self) -> float:
        self.set_gradient()
        return self._gradient

    @property
    def samples(self) -> int:
        return len(self._samples)

    @property
    def samples_raw(self) -> list:
        return self._samples

    @samples_raw.setter
    def samples_raw(self, lst):
        self._samples.extend(lst)
        self.set_gradient()

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

    @property
    def is_clean(self) -> bool:
        return all([time.time() - self._init_time > 300, self.samples > 1])

    def set_gradient(self):
        self._remove_from_list()
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

    def add_reading(self, val: float, t: float = time.time()):
        if self._ignore is None or self._ignore < val:
            self._samples.append((int(t), round(val, 3)))
            self._latest_update = time.time()
            self._remove_from_list()
            self.set_gradient()

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
       self.set_gradient()

    async def async_add_reading(self, val: float, t: float = time.time()):
        self.add_reading(val, t)

    async def async_remove_from_list(self):
        self._remove_from_list()

    def predicted_time_at_value(self, target_value: float) -> datetime|None:
        if self._gradient is None or len(self._samples) < 2:
            return None
        current_gradient = self._gradient
        if current_gradient == 0 or all([
            target_value < 0,
            self._samples[-1][1] > 0,
            current_gradient > 0
            ]):
            return None
        time_diff = timedelta(hours=(target_value - self._samples[-1][1]) / current_gradient)
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


tt = Gradient(max_age=300, max_samples=10, precision=2, ignore=None)
tt.add_reading(50.3, time.time()-3000)
tt.add_reading(50.2, time.time()-2500)
tt.add_reading(50.2, time.time()-2000)
tt.add_reading(50.2, time.time()-1500)
tt.add_reading(50.1, time.time()-1000)
tt.add_reading(49, time.time()-50)
print(f"gradient: {tt.gradient}")