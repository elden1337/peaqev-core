from dataclasses import dataclass, field
from typing import List
from .enums.datepart_datetype import DatePartDateType
from .enums.datepart_modeltype import DatePartModelType
from .enums.dividents import Dividents

@dataclass
class DatePartModel:
    type: DatePartModelType = field(default_factory=lambda : DatePartModelType.Unset)
    dttype:  DatePartDateType = field(default_factory=lambda : DatePartDateType.Unset)
    values: List[int] = field(default_factory=lambda : [])

@dataclass
class Group:
    divident: Dividents = field(default_factory=lambda: Dividents.UNSET)
    dateparts: List[DatePartModel] = field(default_factory=lambda : [DatePartModel()])

@dataclass
class QueryServiceModel:
    groups: List[Group] = field(default_factory=lambda : [Group()])
