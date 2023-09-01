import logging
import time
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)


def dt_from_epoch(epoch: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))

class Gradient:
    def __init__(
        self, max_age: int, max_samples: int, precision: int = 2, ignore: int|None = None
    ):
        self._init_time = time.time()
        self._readings = []
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
        return len(self._readings)

    @property
    def samples_raw(self) -> list:
        return self._readings

    @samples_raw.setter
    def samples_raw(self, lst):
        self._readings.extend(lst)
        self.set_gradient()

    @property
    def oldest_sample(self) -> str:
        if len(self._readings) > 0:
            return dt_from_epoch(self._readings[0][0])
        return str(datetime.min)

    @property
    def newest_sample(self) -> str:
        if len(self._readings) > 0:
            return dt_from_epoch(self._readings[-1][0])
        return str(datetime.min)

    @property
    def is_clean(self) -> bool:
        return all([time.time() - self._init_time > 300, self.samples > 1])

    def set_gradient(self):
        self._remove_from_list()
        temps = self._readings
        if len(temps) == 1:
            self._gradient = 0
        elif len(temps) - 1 > 0:
            try:
                x = (temps[-1][1] - temps[0][1]) / ((time.time() - temps[0][0]) / 3600)
                self._gradient = x
            except ZeroDivisionError as e:
                _LOGGER.warning({e})
                self._gradient = 0

    def add_reading(self, val: float, t: float = time.time()):
        if self._ignore is None or self._ignore < val:
            self._readings.append((int(t), round(val, 3)))
            self._latest_update = time.time()
            self._remove_from_list()
            self.set_gradient()

    def _remove_from_list(self):
        """Removes overflowing number of samples and old samples from the list."""
        while len(self._readings) > self._max_samples:
            self._readings.pop(0)
        gen = (
            x for x in self._readings if time.time() - int(x[0]) > self._max_age
        )
        for i in gen:
            if len(self._readings) > 1:
                # Always keep two readings to be able to calc trend
                self._readings.remove(i)

    async def async_set_gradient(self):
       self.set_gradient()

    async def async_add_reading(self, val: float, t: float = time.time()):
        self.add_reading(val, t)

    async def async_remove_from_list(self):
        self._remove_from_list()

    def predicted_time_at_value(self, target_value: float) -> datetime|None:
        if self._gradient is None or len(self._readings) < 2:
            return None
        current_gradient = self._gradient
        if current_gradient == 0 or all([
            target_value < 0,
            self._readings[-1][1] > 0,
            current_gradient > 0
            ]):
            return None
        time_diff = timedelta(hours=(target_value - self._readings[-1][1]) / current_gradient)
        return datetime.now() + time_diff
        
    def predicted_value_at_time(self, target_time: datetime) -> float|None:
        if self._gradient is None or target_time < datetime.now() or len(self._readings) < 2:
            return None
        current_gradient = self._gradient
        if current_gradient == 0:
            return None
        time_diff = target_time - datetime.now()
        expected_value = self._readings[-1][1] + (current_gradient * time_diff.total_seconds() / 3600)
        return round(expected_value,self._precision)


# tt = Gradient(max_age=300, max_samples=10, precision=2, ignore=None)
# tt.add_reading(867, time.time()-120)
# tt.add_reading(832, time.time()-100)
# tt.add_reading(629, time.time()-83)
# tt.add_reading(649, time.time()-75)
# tt.add_reading(639, time.time()-70)
# tt.add_reading(438, time.time()-60)
# tt.add_reading(457, time.time()-50)
# tt.add_reading(656, time.time()-40)
# tt.add_reading(664, time.time()-30)
# tt.add_reading(636, time.time()-20)
# print(f"gradient: {tt.gradient}")
# print(tt.predicted_time_at_value(-50))
# print(tt.predicted_value_at_time(datetime.now() + timedelta(minutes=6)))