from dataclasses import dataclass
from datetime import datetime
import logging
import time

_LOGGER = logging.getLogger(__name__)


@dataclass
class Day:
    sessions: int
    charge: float


class EnergyWeekly:
    def __init__(self):
        self.model: dict[int, Day] = {}

    async def async_setup(self, incoming_dict: dict | None = None):
        if incoming_dict is not None:
            await self.async_unpack(incoming_dict)
        else:
            await self.async_set_init_model()

    async def async_set_init_model(self):
        ret = {}
        for i in range(0, 7):
            ret[i] = Day(0, 0)
        self.model = ret

    @property
    def export(self) -> dict[int, dict[str, float]]:
        "export the model to HA-friendly states"
        ret = {}
        for idx, m in self.model.items():
            m_ret = {"sessions": m.sessions, "total_charge": m.charge}
            ret[idx] = m_ret
        return ret

    @property
    def average(self) -> float:
        sessions = sum([h.sessions for h in self.model.values()])
        charge = sum([h.charge for h in self.model.values()])
        ret = 0.0
        try:
            ret = charge / sessions
        except:
            _LOGGER.debug(f"Could not calculate average")
        return round(ret, 1)

    @property
    def total_sessions(self) -> int:
        try:
            return sum([h.sessions for h in self.model.values()])
        except:
            _LOGGER.debug("could not retreive sessions.")
            return 0

    @property
    def total_charge(self) -> float:
        try:
            return sum([h.charge for h in self.model.values()])
        except:
            _LOGGER.debug("could not retreive total charge")
            return 0.0

    async def async_unpack(self, incoming: dict) -> dict[int, Day] | None:
        if isinstance(incoming, dict) and len(incoming):
            model = {}
            for i in range(0, 7):
                if i in incoming.keys():
                    m_ret = Day(incoming[i]["sessions"], incoming[i]["total_charge"])
                else:
                    m_ret = Day(0, 0)
                model[i] = m_ret
            self.model = model
        else:
            return await self.async_set_init_model()

    async def async_update(self, _charge: float, mock_time: float | None = None):
        timer = mock_time or time.time()
        if _charge > 0:
            self.model[datetime.fromtimestamp(timer).weekday()].charge += _charge
            self.model[datetime.fromtimestamp(timer).weekday()].sessions += 1

    async def async_average_for_day(self, day: int) -> float:
        try:
            return self.model[day].charge / self.model[day].sessions
        except:
            return 0.0


# EXAMPLE = {
#     0: Day(1,50),
#     1: Day(4,50),
#     2: Day(2,15),
#     3: Day(3,20),
#     4: Day(10,123),
#     5: Day(0,0),
#     6: Day(10, 110)
# }

# EXPORT_EXAMPLE = {0: {'sessions': 1, 'total_charge': 50}, 1: {'sessions': 4, 'total_charge': 50}, 2: {'sessions': 2, 'total_charge': 15}, 3: {'sessions': 3, 'total_charge': 20}, 4: {'sessions': 10, 'total_charge': 123}, 5: {'sessions': 0, 'total_charge': 0}, 6: {'sessions': 10, 'total_charge': 110}}
# EXPORT_MISSING = {0: {'sessions': 1, 'total_charge': 50}, 2: {'sessions': 2, 'total_charge': 15}, 3: {'sessions': 3, 'total_charge': 20}, 4: {'sessions': 10, 'total_charge': 123}, 5: {'sessions': 0, 'total_charge': 0}, 6: {'sessions': 10, 'total_charge': 110}}
# e = EnergyWeekly()
# e.unpack(EXPORT_MISSING)
# print(e.export)
# print(e.model)
# print(e.average)
# print(e.average_for_day(0))
