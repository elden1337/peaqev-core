import logging
from datetime import datetime
from .hubmember import HubMember

_LOGGER = logging.getLogger(__name__)

EXPORT_FACTOR = 0.9

class CurrentPeak(HubMember):
    def __init__(self, data_type: type, initval, startpeaks:dict, options_use_history: bool = False):
        self._options_peaks: dict = startpeaks
        self._value = initval
        self._history: dict[str, float] = {}
        self._active: bool = options_use_history
        super().__init__(data_type, initval)

    @HubMember.value.setter
    def value(self, val): # pylint:disable=invalid-overridden-method
        _val = self._set_value(val)
        if type(_val) is float:
            self.update_history(_val)
        else:
            _LOGGER.error(f"Error in setting value: {val}")

    @property
    def history(self) -> dict:
        return self._history

    def _get_peak(self) -> float:
        try:
            """this one returns the peak which is either the monthly historic peak or the current peak"""
            options_start = self._options_peaks.get(datetime.now().month, self._options_peaks.get(str(datetime.now().month), 0))
            _past_key = self._make_key(datetime.now().year - 1)
            if not self._active or _past_key not in self._history:
                return max(options_start, self._history.get(self._make_key(), 0))
            return max(
                options_start, 
                self._history[_past_key] * EXPORT_FACTOR, 
                self._history.get(self._make_key(), 0)
                )
        except Exception as e:
            _LOGGER.error(f"Error in get_peak: {e}")
            return 0
    
    @staticmethod
    def _make_key(year = datetime.now().year) -> str:
        return f"{str(year)}_{str(datetime.now().month)}"

    async def async_update(self, peak: float) -> None:
        self.update_history(peak)

    def update_history(self, peak: float) -> None:
        _key = self._make_key()
        self._history[_key] = max(self._history.get(_key, 0), peak)
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
                self._history[month] = importdto[month]
        if len(validation_errors):
            ret["status"] = "Error"
            ret["errors"] = validation_errors
        else:
            ret["status"] = "OK"
            ret["errors"] = ["No errors"]
        self._value = self._get_peak()
        return ret

    def _validate_value(self, monthkey: str, value: any, validation_errors: list) -> bool: # type: ignore
        """check if value is valid"""
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
