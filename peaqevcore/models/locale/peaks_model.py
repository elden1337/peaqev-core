from dataclasses import dataclass
from datetime import datetime


@dataclass
class PeaksModel:
    _p: dict
    _m: int = 0
    _is_dirty: bool = False

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    @is_dirty.setter
    def is_dirty(self, value: bool) -> None:
        if value:
            self._is_dirty = value

    @property
    def p(self) -> dict:
        return self._p

    @property
    def m(self) -> int:
        return self._m

    @property
    def export_peaks(self) -> dict:
        return {
            "m": self._m,
            "p": dict([(f"{pp[0]}h{pp[1]}", self._p.get(pp)) for pp in self._p]),
        }

    @property
    def max_value(self) -> float | None:
        return None if len(self._p) == 0 else max(self._p.values())

    @property
    def min_value(self) -> float | None:
        return None if len(self._p) == 0 else min(self._p.values())

    @property
    def value_avg(self) -> float:
        if len(self._p) == 0:
            return 0
        return sum(self._p.values()) / len(self._p)

    def remove_min(self) -> dict:
        self._p.pop(min(self._p, key=self._p.get))
        return self._p

    async def async_set_init_dict(self, dict_data: dict, dt=datetime.now(), override:bool = False) -> None:
        ppdict = dict()
        self._m = dict_data.get("m")
        if dt.month != self.m:
            await self.async_reset()
        else:
            for pp in dict_data.get("p"):
                tkeys = pp.split("h")
                ppkey = (int(tkeys[0]), int(tkeys[1]))
                p: dict = dict_data.get("p")
                ppdict[ppkey] = p.get(pp)
            if len(self._p) and not override:
                self._p = dict(self._p.items() | ppdict.items())
            else:
                self._p = ppdict
            self._m = dict_data.get("m")
            self.is_dirty = True

    async def async_add_kv_pair(self, key: any, value: any) -> dict:
        try:
            self._p[key] = value
            return self._p
        except KeyError:
            raise Exception(f"Invalid key '{key}'")
        except ValueError:
            raise Exception(f"Invalid value '{value}'")

    async def async_set_month(self, value: int) -> None:
        if value:
            self._m = value

    async def async_remove_min(self) -> dict:
        self._p.pop(min(self._p, key=self._p.get))
        return self._p

    async def async_pop_key(self, key: any) -> dict:
        if key:
            try:
                self._p.pop(key)
                return self._p
            except KeyError:
                raise Exception(f"Key '{key}' does not exist.")
        raise Exception("Expected key but received none.")

    async def async_reset(self) -> None:
        self._m = datetime.now().month
        self.is_dirty = False
        self._p = {}

    async def async_clear(self) -> None:
        self._p.clear()
