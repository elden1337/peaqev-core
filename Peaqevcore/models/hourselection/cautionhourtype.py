from enum import Enum

class CautionHourType(Enum):
    SUAVE = "Suave"
    INTERMEDIATE = "Intermediate"
    AGGRESSIVE = "Aggressive"

    @staticmethod
    def get_num_value(type):
        values = {
            CautionHourType.SUAVE: 0.75,
            CautionHourType.INTERMEDIATE: 0.5,
            CautionHourType.AGGRESSIVE: 0.4
            }
        return values[type]