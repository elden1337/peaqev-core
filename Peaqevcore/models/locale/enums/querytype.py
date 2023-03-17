from enum import Enum

class QueryType(Enum):
    AverageOfThreeHours = 0
    AverageOfThreeDays = 1
    AverageOfFiveDays = 2
    Max = 3