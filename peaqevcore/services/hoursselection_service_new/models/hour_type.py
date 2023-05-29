from enum import Enum


class HourType(Enum):
    Regular = 0
    AboveMax = 1
    BelowMin = 2