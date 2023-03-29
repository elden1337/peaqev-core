from ...PeaqErrors import PeaqKeyError, PeaqValueError
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

@dataclass
class PeaksModel:
    _peaks_dict: dict
    _m: int = 0
    _is_dirty: bool = False

    def set_init_dict(self, dict_data:Dict, dt=datetime.now()) -> None:
        ppdict = {}
        if dt.month != self.month:
            self.reset()
        else:
            for pp in dict_data.get("p"):
                tkeys = pp.split("h")
                ppkey = (int(tkeys[0]), int(tkeys[1]))
                ppdict[ppkey] = dict_data.get("p").get(pp)
            if len(self._peaks_dict):
                self._peaks_dict = dict(self._peaks_dict.items() | ppdict.items())
            else: 
                self._peaks_dict = ppdict
            self._month = dict_data.get("m")
            self.is_dirty = True

    async def async_set_init_dict(self, dict_data:Dict, dt=datetime.now()) -> bool:
        ppdict = {}
        if dt.month != self.month:
            await self.async_reset()
        else:
            for pp in dict_data.get("p"):
                tkeys = pp.split("h")
                ppkey = (int(tkeys[0]), int(tkeys[1]))
                ppdict[ppkey] = dict_data.get("p").get(pp)
            if len(self._peaks_dict):
                self._peaks_dict = dict(self._peaks_dict.items() | ppdict.items())
            else: 
                self._peaks_dict = ppdict
            self._month = dict_data.get("m")
            self.is_dirty = True
        return True

    @property
    def p(self) -> dict:
        return self._peaks_dict
  
    @property
    def m(self) -> int:
        return self._month

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    @is_dirty.setter
    def is_dirty(self, value: bool) -> None:
        if value:
            self._is_dirty = value

    @property
    def export_peaks(self) -> dict:
        return {
            "m": self._month,
            "p": {[(f"{pp[0]}h{pp[1]}", self._peaks_dict.get(pp)) for pp in self._peaks_dict]}
        }

    @property
    def max_value(self) -> any:
        return None if len(self._peaks_dict) == 0 else max(self._peaks_dict.values())

    @property
    def min_value(self) -> any:
        return None if len(self._peaks_dict) == 0 else min(self._peaks_dict.values())

    @property
    def value_avg(self) -> float:
        if len(self._peaks_dict) == 0:
            return 0
        return sum(self._peaks_dict.values()) / len(self._peaks_dict)

    def set_month(self, value: int) -> None:
        if value:
            self._month = value

    def remove_min(self) -> dict:
        self._peaks_dict.pop(min(self._peaks_dict, key=self._peaks_dict.get))
        return self._peaks_dict

    def add_kv_pair(self, key: any, value: any) -> dict:
        try:
            self._peaks_dict[key] = value
            return self._peaks_dict
        except KeyError:
            raise PeaqKeyError(f"Invalid key '{key}'")
        except ValueError:
            raise PeaqValueError(f"Invalid value '{value}'")

    def pop_key(self, key: any) -> dict:
        if key:
            try:
                self._peaks_dict.pop(key)
                return self._peaks_dict
            except KeyError:
                raise PeaqValueError(f"Key '{key}' does not exist.")
        raise PeaqValueError("Expected key but received none.")

    def reset(self) -> None:
        self._month = datetime.now().month
        self.is_dirty = False
        self._peaks_dict = {}

    async def async_reset(self) -> None:
        self._month = datetime.now().month
        self.is_dirty = False
        self._peaks_dict = {}

    def clear(self) -> None:
        self._peaks_dict.clear()