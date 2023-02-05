from enum import Enum

class CautionHourType(Enum):
    SUAVE = "suave"
    INTERMEDIATE = "intermediate"
    AGGRESSIVE = "aggressive"

    @staticmethod
    def get_num_value(type_state):
        if isinstance(type_state, str):
            tt = type_state.lower()
        elif isinstance(type_state, CautionHourType):
            tt = type_state.value
        else:
            print(f"type of {type_state} is {type(type_state)}")
            raise ValueError
        
        return VALUES_CONVERSION[tt]

VALUES_CONVERSION = {
            CautionHourType.SUAVE.value: 0.75,
            CautionHourType.INTERMEDIATE.value: 0.5,
            CautionHourType.AGGRESSIVE.value: 0.4
            }
