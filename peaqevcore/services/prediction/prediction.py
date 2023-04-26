from datetime import datetime
from ...util import async_convert_quarterly_minutes, _convert_quarterly_minutes


class Prediction:
    def __init__(self, hub=None):
        self._hub = hub

    @staticmethod
    async def async_predicted_energy(
        now_min: int | None = None,
        now_sec: int | None = None,
        power_avg: float = 0,
        total_hourly_energy: float = 0,
        is_quarterly: bool = False,
    ) -> float:
        """This method does allow for negative energy, ie from solar panels being read."""
        _now_min = now_min or datetime.now().minute
        _now_sec = now_sec or datetime.now().second

        if _now_min not in range(0, 60):
            raise ValueError(f"Value 'now_min' ({_now_min}) must be between (0..60]")
        if _now_sec not in range(0, 60):
            raise ValueError(f"Value 'now_max' ({_now_sec}) must be between (0..60]")

        minute = await async_convert_quarterly_minutes(_now_min, is_quarterly)

        if total_hourly_energy != 0 and (minute > 0 or (minute + _now_sec) > 30):
            ret = (
                (power_avg / 60 / 60) * (3600 - ((minute * 60) + _now_sec))
                + total_hourly_energy * 1000
            ) / 1000
        else:
            ret = power_avg / 1000
        return round(ret, 3)

    @staticmethod
    async def async_predicted_percentage_of_peak(
        peak: float, predicted_energy: float
    ) -> float:
        if peak == 0.0 or peak is None:
            return 0
        elif predicted_energy <= 0.0 or predicted_energy is None:
            return 0
        return round((predicted_energy / peak) * 100, 2)

    # legacy

    @property
    def predictedenergy(self) -> float:
        """legacy. remove once peaqhvac is async."""
        return Prediction._predicted_energy(
            datetime.now().minute,
            datetime.now().second,
            self._hub.sensors.powersensormovingaverage.value
            if hasattr(self._hub.sensors, "powersensormovingaverage")
            else 0,
            self._hub.sensors.totalhourlyenergy.value,
            # self._hub.sensors.locale.data.is_quarterly(self._hub.sensors.locale.data),
        )

    @property
    def predictedpercentageofpeak(self) -> float:
        """legacy. remove once peaqhvac is async."""
        if hasattr(self._hub.sensors, "current_peak"):
            return Prediction._predicted_percentage_of_peak(
                self._hub.sensors.current_peak.value, self.predictedenergy
            )
        return 0.0

    @staticmethod
    def _predicted_energy(
        now_min: int,
        now_sec: int,
        power_avg: float,
        total_hourly_energy: float,
        is_quarterly: bool = False,
    ) -> float:
        """legacy. remove once peaqhvac is async."""
        if now_min not in range(0, 60):
            raise Exception(f"Value 'now_min' ({now_min}) must be between (0..60]")
        if now_sec not in range(0, 60):
            raise Exception(f"Value 'now_max' ({now_sec}) must be between (0..60]")

        minute = _convert_quarterly_minutes(now_min, is_quarterly)

        if total_hourly_energy != 0 and (minute > 0 or (minute + now_sec) > 30):
            ret = (
                (power_avg / 60 / 60) * (3600 - ((minute * 60) + now_sec))
                + total_hourly_energy * 1000
            ) / 1000
        else:
            ret = power_avg / 1000
        return round(ret, 3)

    @staticmethod
    def _predicted_percentage_of_peak(peak: float, predicted_energy: float) -> float:
        """legacy. remove once peaqhvac is async."""
        if peak == 0.0 or peak is None:
            return 0
        elif predicted_energy <= 0.0 or predicted_energy is None:
            return 0
        return round((predicted_energy / peak) * 100, 2)
