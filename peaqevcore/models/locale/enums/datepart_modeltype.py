from enum import Enum

class DatePartModelType(Enum):
    GreaterOrEqual = "gteq"
    LessOrEqual = "lteq"
    In = "in"
    Equal = "eq"
    Less = "lt"
    Greater = "gt"
    Not = "not"
    Unset = ""