import time
from statistics import mean

class Average:
    def __init__(self, max_age: int, max_samples: int, precision: int = 2):
        self._readings = []
        self._average = 0
        self._smooth_average = 0
        self._max_age = max_age
        self._max_samples = max_samples
        self._precision = precision
        self._latest_update = 0

    @property
    def average(self) -> float:
        self._set_average()
        return round(self._average, self._precision)
    
    @property
    def smooth_average(self) -> float:
        self._set_smooth_average()
        return round(self._smooth_average, self._precision)

    def _set_smooth_average(self):
        x=0.1
        i = 1
        moving_averages = []
        moving_averages.append(self._readings[0][1])
        while i < len(self._readings):
            window_average = round((x*self._readings[i][1])+(1-x)*moving_averages[-1], 2)
            moving_averages.append(window_average)
            i += 1
        self._smooth_average = moving_averages[-1]
        
    def _set_average(self):
        try:
            self._average = mean([x[1] for x in self._readings])
        except ZeroDivisionError:
            self._average = 0

    def _remove_from_list(self):
        """Removes overflowing number of samples and old samples from the list."""
        while len(self._readings) > self._max_samples:
            self._readings.pop(0)
        gen = (
            x for x in self._readings if time.time() - int(x[0]) > self._max_age
        )
        for i in gen:
            if len(self._readings) > 1:
                # Always keep one reading
                self._readings.remove(i)

    def add_reading(self, val: float):
        self._readings.append((int(time.time()), round(val, 3)))
        self._latest_update = time.time()
        self._remove_from_list()
        self._set_average()

#------------
# from random import randrange

# a = Average(300, 200)
# averages = []
# smooth_averages = []

# for i in range(3600):
#     val = randrange(250, 1000)
#     a.add_reading(val)
   
#     averages.append(a.average)
#     smooth_averages.append(a.smooth_average)
#     #time.sleep(0.01)


# import matplotlib.pyplot as plt
# plt.plot(averages)
# plt.plot(smooth_averages)
# #plt.plot(averages2)
# #plt.plot(averages3)
# #plt.plot(maxes)
# #plt.plot(mins)
# plt.show()