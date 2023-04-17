import logging
from dataclasses import dataclass, field
from typing import List, Dict
from .hourobjects.hourobject import HourObject
from .hourtypelist import HourTypeList

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=False)
class HoursModel:
    non_hours: List[int] = field(default_factory=lambda : [])
    caution_hours: List[int] = field(default_factory=lambda : [])
    dynamic_caution_hours: Dict[int, float] = field(default_factory=lambda : {})
    hours_today: HourObject = field(default_factory=lambda : HourObject([],[],dict()))
    hours_tomorrow: HourObject = field(default_factory=lambda : HourObject([],[],dict()))
    offset_dict: Dict[Dict[str,float], Dict[str, float]] = field(default_factory=lambda: {})

    async def async_update_non_hours(self,hour:int) -> None:
        ret = []
        ret.extend(h for h in self.hours_today.nh if h >= hour)
        ret.extend(h for h in self.hours_tomorrow.nh if h < hour)
        self.non_hours = ret
    
    def _update_non_hours(self,hour:int) -> None:
        ret = []
        ret.extend(h for h in self.hours_today.nh if h >= hour)
        ret.extend(h for h in self.hours_tomorrow.nh if h < hour)
        self.non_hours = ret

    async def async_update_caution_hours(self, hour:int) -> None:
        ret = []
        ret.extend(h for h in self.hours_today.ch if h >= hour)
        ret.extend(h for h in self.hours_tomorrow.ch if h < hour)
        self.caution_hours = ret

    def _update_caution_hours(self, hour:int) -> None:
        ret = []
        ret.extend(h for h in self.hours_today.ch if h >= hour)
        ret.extend(h for h in self.hours_tomorrow.ch if h < hour)
        self.caution_hours = ret

    async def async_update_dynamic_caution_hours(self, hour:int) -> None:
        ret = {}
        ret.update({k: v for k, v in self.hours_today.dyn_ch.items() if k >= hour and k not in self.hours_today.nh})
        ret.update({k: v for k, v in self.hours_tomorrow.dyn_ch.items() if k < hour and k not in self.hours_tomorrow.nh})
        self.dynamic_caution_hours = ret

    def _update_dynamic_caution_hours(self, hour:int) -> None:
        ret = {}
        ret.update({k: v for k, v in self.hours_today.dyn_ch.items() if k >= hour and k not in self.hours_today.nh})
        ret.update({k: v for k, v in self.hours_tomorrow.dyn_ch.items() if k < hour and k not in self.hours_tomorrow.nh})
        self.dynamic_caution_hours = ret

    async def async_update_offset_dict(self) -> None:
        ret = {}
        ret['today'] = self.hours_today.offset_dict
        ret['tomorrow'] = self.hours_tomorrow.offset_dict
        self.offset_dict = ret

    async def async_touch_midnight(self) -> bool:
        self.hours_today = self.hours_tomorrow
        self.hours_tomorrow = HourObject([], [], {})
        self.offset_dict["today"] = self.offset_dict.get("tomorrow", {})
        self.offset_dict["tomorrow"] = {}
        return True

    async def async_update_hour_lists(self, hour:int) -> None:
        await self.async_update_non_hours(hour)
        await self.async_update_caution_hours(hour)
        await self.async_update_dynamic_caution_hours(hour)
        await self.async_update_offset_dict()

    def update_hour_list(self, hour:int, listtype:HourTypeList = None) -> None:
        match listtype:
            case HourTypeList.NonHour:
                self._update_non_hours(hour)
            case HourTypeList.CautionHour:
                self._update_caution_hours(hour)
            case HourTypeList.DynCautionHour:
                self._update_dynamic_caution_hours(hour)   
            case _:
                pass