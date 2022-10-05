from enum import Enum
from const import (
    CAUTIONHOURTYPE_SUAVE,
    CAUTIONHOURTYPE_INTERMEDIATE,
    CAUTIONHOURTYPE_AGGRESSIVE
)

class CautionHourType(Enum):
    Suave = CAUTIONHOURTYPE_SUAVE
    Intermediate = CAUTIONHOURTYPE_INTERMEDIATE
    Aggressive = CAUTIONHOURTYPE_AGGRESSIVE


ttt = CautionHourType(CAUTIONHOURTYPE_SUAVE)
#detta är enumvärdet
print(ttt.name)
#detta är strängen
print(ttt.value)