from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from .hour_price import HourPrice
from .datetime_model import DateTimeModel


class AllowanceType(Enum):
    StoppedUntil = "Stopped until "
    AllowedUntil = "Allowed until "
    StoppedUntilTomorrow = "Stopped until tomorrow at "
    AllowedUntilTomorrow = "Allowed until tomorrow at "
    StoppedUntilFurtherNotice = "Stopped until further notice."
    AllowedUntilFurtherNotice = "Allowed until further notice."


@dataclass
class AllowanceObj:
    prefix_type: AllowanceType
    display_name: str = field(init=False)
    hour: int = -1
    quarter: int = -1
    datum: date = date.today()

    def __post_init__(self):
        # set display name
        match self.prefix_type:
            case AllowanceType.StoppedUntil | AllowanceType.AllowedUntil:
                self.display_name = f"{self.prefix_type.value}{self.__set_num_value(self.hour)}:{self.__set_num_value(self.quarter * 15)}."
            case AllowanceType.StoppedUntilTomorrow | AllowanceType.AllowedUntilTomorrow:
                self.display_name = (
                    f"{self.prefix_type.value}{self.__set_num_value(self.hour)}:00."
                )
            case AllowanceType.StoppedUntilFurtherNotice | AllowanceType.AllowedUntilFurtherNotice:
                self.display_name = self.prefix_type.value

    def __set_num_value(self, hour: int):
        _h = str(hour)
        if len(_h) == 1:
            return f"0{_h}"
        return _h


def set_allowance_obj(
    dtmodel: DateTimeModel, future_hours: list[HourPrice]
) -> AllowanceObj:
    if not len([hp.dt for hp in future_hours if hp.permittance > 0.0]):
        return AllowanceObj(AllowanceType.StoppedUntilFurtherNotice)
    if not len([hp.dt for hp in future_hours if hp.permittance == 0.0]):
        return AllowanceObj(AllowanceType.AllowedUntilFurtherNotice)
    first_start = min([hp.dt for hp in future_hours if hp.permittance > 0.0])
    _stopped = first_start != dtmodel.dt
    if _stopped:
        if first_start.date() > dtmodel.hdate:
            return AllowanceObj(
                AllowanceType.StoppedUntilTomorrow, hour=first_start.hour
            )
        else:
            return AllowanceObj(
                AllowanceType.StoppedUntil,
                hour=first_start.hour,
                quarter=first_start.minute // 15,
            )
    else:
        first_stop = min([hp.dt for hp in future_hours if hp.permittance == 0.0])
        if first_stop.date() > dtmodel.hdate:
            return AllowanceObj(
                AllowanceType.AllowedUntilTomorrow, hour=first_stop.hour
            )
        else:
            return AllowanceObj(
                AllowanceType.AllowedUntil,
                hour=first_stop.hour,
                quarter=first_stop.minute // 15,
            )
