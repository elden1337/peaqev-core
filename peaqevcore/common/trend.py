import logging
import math
from statistics import mean
import time
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

MIN_SAMPLES = 2

def dt_from_epoch(epoch: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))

class Gradient:
    def __init__(
        self, 
        max_age: int, 
        max_samples: int, 
        precision: int = 2,
        ignore: int|None = None, 
        outlier: float|None = None,
        smoothing_average: int = 1
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
        self._smoothing_average = smoothing_average

    @property
    def trend(self) -> float:
        return self._calculate_trend(use_decay=True)
    
    def _calculate_trend(self, use_decay: bool = False) -> float:
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
            time_since_last_sample = time.time() - self._latest_update
            decay_factor = math.exp(-time_since_last_sample / (60 * 60))  # Decay over an hour

            if use_decay:
                slope *= decay_factor

            if self._smoothing_average > 1:
                smoothed_slope = mean([slope] + [data[i][1] - data[i-self._smoothing_average][1] for i in range(self._smoothing_average, n)])
                ret = round(smoothed_slope, self._precision)
            else:
                ret = round(slope, self._precision)

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
                ss = sorted(values, key=lambda x: x[0])
                x = (ss[-1][1] - ss[0][1]) / ((time.time() - ss[0][0]) / 3600)
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
                self._latest_update = t
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





# ttt = [
#     - - 1701543099,
#   - 19.671,
# - - 1701542878,
#   - 19.7,
# - - 1701542747,
#   - 19.686,
# - - 1701542222,
#   - 19.7,
# - - 1701542215,
#   - 19.714,
# - - 1701542172,
#   - 19.729,
# - - 1701541371,
#   - 19.743,
# - - 1701541280,
#   - 19.729,
# - - 1701541181,
#   - 19.743,
# - - 1701539524,
#   - 19.757,
# - - 1701539478,
#   - 19.771,
# - - 1701539458,
#   - 19.786,
# - - 1701539338,
#   - 19.8,
# - - 1701539110,
#   - 19.814,
# - - 1701538982,
#   - 19.829,
# - - 1701538025,
#   - 19.814,
# - - 1701537533,
#   - 19.8,
# - - 1701537525,
#   - 19.814,
# - - 1701537263,
#   - 19.829,
# - - 1701537085,
#   - 19.857,
# - - 1701536982,
#   - 19.871,
# - - 1701536658,
#   - 19.886,
# - - 1701536226,
#   - 20.25,
# - - 1701536226,
#   - 20.2,
# - - 1701536226,
#   - 20.175,
# - - 1701536226,
#   - 20.06,
# - - 1701536226,
#   - 19.95,
# - - 1701536226,
#   - 19.9,
# - - 1701536019,
#   - 19.9,
# - - 1701536004,
#   - 19.929,
# - - 1701535978,
#   - 19.957,
# - - 1701535944,
#   - 19.971,
# ]

# ret = {}

# for idx, i in enumerate(ttt):
#     if idx % 2 == 0:
#         tt = i
#         ret[idx] = [tt]
#     else:
#         ret[idx-1].append(-float(i))

# tt = Gradient(max_age=7200, max_samples=100, precision=1)
# tt2 = Gradient(max_age=7200, max_samples=100, precision=1, smoothing_average=6)

# tt_values = []
# tt2_values = []
# x_values = []

# t = time.time()-3599
# tt.add_reading(54,t)
# tt2.add_reading(54,t)
# tt_values.append(tt.trend)
# tt2_values.append(tt2.trend)
# x_values.append(t)

# t = time.time()-3479
# tt.add_reading(53.8,t)
# tt2.add_reading(53.8,t)
# tt_values.append(tt.trend)
# tt2_values.append(tt2.trend)
# x_values.append(t)

# t = time.time()-3359
# tt.add_reading(53.8,t)
# tt2.add_reading(53.8,t)
# tt_values.append(tt.trend)
# tt2_values.append(tt2.trend)
# x_values.append(t)

# t = time.time()-3260
# tt.add_reading(53.1,t)
# tt2.add_reading(53.1,t)
# tt_values.append(tt.trend)
# tt2_values.append(tt2.trend)
# x_values.append(t)

# t = time.time()-3140
# tt.add_reading(53,t)
# tt2.add_reading(53,t)
# tt_values.append(tt.trend)
# tt2_values.append(tt2.trend)
# x_values.append(t)

# t = time.time()-3020
# tt.add_reading(53,t)
# tt2.add_reading(53,t)
# tt_values.append(tt.trend)
# tt2_values.append(tt2.trend)
# x_values.append(t)

# t = time.time()-2700
# tt.add_reading(52,t)
# tt2.add_reading(52,t)
# tt_values.append(tt.trend)
# tt2_values.append(tt2.trend)
# x_values.append(t)

# import matplotlib.pyplot as plt

# # Convert the timestamps to a more readable format
# x_values_readable = [datetime.fromtimestamp(x) for x in x_values]

# plt.figure(figsize=(10, 6))

# # Plot tt_values
# plt.plot(x_values_readable, tt_values, label='tt_values')

# # Plot tt2_values
# plt.plot(x_values_readable, tt2_values, label='tt2_values')

# plt.xlabel('Time')
# plt.ylabel('Values')
# plt.title('tt_values and tt2_values over time')
# plt.legend()

# #plt.show()

# print(tt_values)
# print(tt2_values)