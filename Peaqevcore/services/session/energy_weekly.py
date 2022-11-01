from dataclasses import dataclass
from datetime import datetime
import logging

_LOGGER = logging.getLogger(__name__)

@dataclass
class Day:
    sessions: int
    charge: float


class EnergyWeekly:
    model: dict[int, Day]

    def __init__(self, incoming_dict: dict = None):
        if incoming_dict is not None:
            self.unpack(incoming_dict)
        else:
            self.model = {}

    @property
    def export(self) -> dict[int, dict[str, float]]:
        "export the model to HA-friendly states"
        ret = {}
        for idx, m in self.model.items():
            m_ret = {
                "sessions": m.sessions,
                "total_charge": m.charge
            }
            ret[idx] = m_ret

    @property
    def average(self) -> float:
        sessions = sum([h.sessions for h in self.model.values()])
        charge = sum([h.charge for h in self.model.values()])
        try:
            return round(charge/sessions,1)
        except:
            return 0.0
        
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

    def unpack(self, incoming: dict) -> dict[int, Day]:
        model = {}
        for idx, m in incoming.items():
            m_ret = Day(m["sessions"], m["total_charge"])
            model[idx] = m_ret
        self.model = model

    def update(self, charge:float):
        self.model[datetime.now().weekday()].charge += charge
        self.model[datetime.now().weekday()].sessions += 1

    def average_for_day(self, day: int) -> float:
        try:
            return self.model[day].charge/self.model[day].sessions
        except:
            print("error")
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

# e = EnergyWeekly(EXPORT_EXAMPLE)
# print(e.model)
# print(e.average)
# print(e.average_for_day(0))