import logging
from datetime import datetime
from .hubmember import HubMember
from statistics import mean
_LOGGER = logging.getLogger(__name__)

EXPORT_FACTOR = 0.9

class CurrentPeak(HubMember):
    def __init__(self, data_type: type, initval, startpeaks:dict, options_use_history: bool = False):
        self._options_peaks: dict = startpeaks
        self._value = initval
        self._history: dict[str, list[float|int]] = {}
        self._active: bool = options_use_history
        super().__init__(data_type, initval)

    @HubMember.value.setter
    def value(self, val): # pylint:disable=invalid-overridden-method
        self._value = val
        self.update_history([val] if not isinstance(val, list) else val)

    @property
    def history(self) -> dict:
        return self._history

    def _get_peak(self) -> float:
        try:
            options_start = self._options_peaks.get(datetime.now().month, self._options_peaks.get(str(datetime.now().month), 0))
            past_key = self._make_key(datetime.now().year - 1)
            current_key = self._make_key()
            past_mean = mean(self._history.get(past_key, [0]))
            current_mean = mean(self._history.get(current_key, [0]))
            max_mean = max(past_mean, current_mean)
            if max_mean == past_mean and past_mean > options_start:
                print(f"returning last years * factor. past_mean = {past_mean}, options_start = {options_start}, current_mean = {current_mean} given values {self._history.get(current_key, [0])}")
                return min(self._history[past_key]) * EXPORT_FACTOR
            elif max_mean == current_mean and current_mean > options_start:
                print("returning current mean")
                return min(self._history[current_key])
            else:
                print("returning options start")
                return options_start
        except Exception as e:
            _LOGGER.error(f"Error in get_peak: {e}")
            return 0
    
    @staticmethod
    def _make_key(year = datetime.now().year) -> str:
        return f"{str(year)}_{str(datetime.now().month)}"

    async def async_update(self, peaks: list) -> None:
        self.update_history(peaks)

    def update_history(self, peaks: list) -> None:
        _key = self._make_key()
        self._history[_key] = peaks
        self._value = self._get_peak()

    def import_from_service(self, importdto: dict) -> dict:
        """Import the dict passed from service or on loading hass"""
        ret = {}
        validation_errors = []
        for month in importdto.keys():
            if all([
                self._validate_month(month, validation_errors),
                self._validate_value(month, importdto[month], validation_errors)
            ]):
                self._history[month] = self._set_history_value(importdto[month])
        if len(validation_errors):
            ret["status"] = "Error"
            ret["errors"] = validation_errors
        else:
            ret["status"] = "OK"
            ret["errors"] = ["No errors"]
        self._value = self._get_peak()
        return ret

    def _set_history_value(self, value: float|int|list) -> list:
        if isinstance(value,float|int):
            return [value]
        if isinstance(value, list):
            return value

    def _validate_value(self, monthkey: str, value: any, validation_errors: list) -> bool: # type: ignore
        """check if value is valid"""
        if isinstance(value, list):
            for _value in value:
                if not self._validate_value(monthkey, _value, validation_errors):
                    return False
            return True
        try:
            _value = float(value)
            if _value < 0:
                validation_errors.append(f"Invalid value: {monthkey} - {value}")
                return False
            return True
        except Exception as e:
            validation_errors.append(f"Error with value ({e}): {monthkey} - {value}")
            return False

    def _validate_month(self, monthkey: str, validation_errors: list) -> bool:
        """check if monthkey is valid"""
        _components = monthkey.split("_")
        if len(_components) != 2:
            validation_errors.append(f"Invalid monthkey: {monthkey}")
            return False
        try:
            _year = int(_components[0])
            _month = int(_components[1])
            if any(
                [
                    _year > datetime.now().year, 
                    _year == datetime.now().year and _month > datetime.now().month
                ]):
                validation_errors.append(f"Period is in the future. Cannot add to history: {monthkey}")
                return False
            if _month > 12:
                validation_errors.append(f"Invalid month: {monthkey}")
                return False
            return True
        except Exception as e:
            validation_errors.append(f"Error with month ({e}): {monthkey}")
            return False
