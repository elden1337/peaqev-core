from ...PeaqErrors import PeaqKeyError, PeaqValueError
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PeaksModel:
    _p: dict
    _m: int = 0
    _is_dirty: bool = False

    async def async_set_init_dict(self, dict_data:dict, dt=datetime.now()) -> None:
        ppdict = dict()
        self._m = dict_data.get("m")
        if dt.month != self.m:
            await self.async_reset()
        else:
            for pp in dict_data.get("p"):
                tkeys = pp.split("h")
                ppkey = (int(tkeys[0]), int(tkeys[1]))
                ppdict[ppkey] = dict_data.get("p").get(pp)
            if len(self._p):
                self._p = dict(self._p.items() | ppdict.items())
                print(f"new existing: {self._p}")
            else: 
                self._p = ppdict
            self._m = dict_data.get("m")
            self.is_dirty = True

    def set_init_dict(self, dict_data:dict, dt=datetime.now()) -> None:
        ppdict = dict()
        self._m = dict_data.get("m")
        if dt.month != self.m:
            self.reset()
        else:
            for pp in dict_data.get("p"):
                tkeys = pp.split("h")
                ppkey = (int(tkeys[0]), int(tkeys[1]))
                ppdict[ppkey] = dict_data.get("p").get(pp)
            if len(self._p):
                self._p = dict(self._p.items() | ppdict.items())
                print(f"new existing: {self._p}")
            else: 
                self._p = ppdict
            self._m = dict_data.get("m")
            self.is_dirty = True

    @property
    def p(self) -> dict:
        return self._p

    def add_kv_pair(self, key: any, value: any) -> dict:
        try:
            self._p[key] = value
            return self._p
        except KeyError:
            raise PeaqKeyError(f"Invalid key '{key}'")
        except ValueError:
            raise PeaqValueError(f"Invalid value '{value}'")
            
    @property
    def m(self) -> int:
        return self._m

    def set_month(self, value: int) -> None:
        if value:
            self._m = value

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
            "m": self._m,
            "p": dict(
                [(f"{pp[0]}h{pp[1]}", self._p.get(pp)) for pp in self._p]
                )
        }

    @property
    def max_value(self) -> any:
        return None if len(self._p) == 0 else max(self._p.values())

    @property
    def min_value(self) -> any:
        return None if len(self._p) == 0 else min(self._p.values())

    @property
    def value_avg(self) -> float:
        if len(self._p) == 0:
            return 0
        return sum(self._p.values()) / len(self._p)

    def remove_min(self) -> dict:
        self._p.pop(min(self._p, key=self._p.get))
        return self._p

    def pop_key(self, key: any) -> dict:
        if key:
            try:
                self._p.pop(key)
                return self._p
            except KeyError:
                raise PeaqValueError(f"Key '{key}' does not exist.")
        raise PeaqValueError("Expected key but received none.")

    def reset(self) -> None:
        self._m = datetime.now().month
        self.is_dirty = False
        self._p = {}

    async def async_reset(self) -> None:
        self._m = datetime.now().month
        self.is_dirty = False
        self._p = {}

    def clear(self) -> None:
        self._p.clear()
