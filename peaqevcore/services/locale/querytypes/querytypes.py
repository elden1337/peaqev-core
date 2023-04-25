from ....models.locale.enums.querytype import QueryType
from ....models.locale.enums.sum_types import SumTypes
from ....models.locale.enums.time_periods import TimePeriods
from ....models.locale.sumcounter import SumCounter
from ..locale_query import LocaleQuery

QUERYTYPES = {
    QueryType.AverageOfThreeHours: LocaleQuery(
        sum_type=SumTypes.Avg,
        time_calc=TimePeriods.Hourly,
        cycle=TimePeriods.Monthly,
        sum_counter=SumCounter(counter=3, groupby=TimePeriods.Hourly),
    ),
    QueryType.AverageOfThreeDays: LocaleQuery(
        sum_type=SumTypes.Avg,
        time_calc=TimePeriods.Hourly,
        cycle=TimePeriods.Monthly,
        sum_counter=SumCounter(counter=3, groupby=TimePeriods.Daily),
    ),
    QueryType.Max: LocaleQuery(
        sum_type=SumTypes.Max, time_calc=TimePeriods.Hourly, cycle=TimePeriods.Monthly
    ),
    QueryType.AverageOfFiveDays: LocaleQuery(
        sum_type=SumTypes.Avg,
        time_calc=TimePeriods.Hourly,
        cycle=TimePeriods.Monthly,
        sum_counter=SumCounter(counter=5, groupby=TimePeriods.Daily),
    ),
}
