from datetime import datetime
from typing import List
from ....models.locale.enums.dividents import Dividents
from ....models.locale.enums.datepart_modeltype import DatePartModelType
from ....models.locale.enums.datepart_datetype import DatePartDateType
from ....models.locale.queryservice_model import QueryServiceModel


class QueryService:
    def __init__(self, args: QueryServiceModel = QueryServiceModel()):
        self._settings = args

    async def async_should_register_peak(self, dt: datetime) -> bool:
        main_ret = []
        for s in [
            s for s in self._settings.groups if s.divident is not Dividents.UNSET
        ]:
            group_ret = []
            grouping = (a for a in s.dateparts if len(a.values))
            for a in grouping:
                group_ret.append(
                    await QueryService.async_datepart(a.type, a.dttype, a.values, dt)
                )
            if s.divident is Dividents.AND:
                main_ret.append(all(group_ret))
            else:
                main_ret.append(any(group_ret))
        print(main_ret)
        return any(main_ret) if len(main_ret) else True

    @staticmethod
    async def async_datepart(
        logic: str, dtpart: str, arguments: List[int], timer: datetime
    ) -> bool:
        if not arguments:
            return True
        try:
            arg = arguments if len(arguments) > 1 else arguments[0]
            _logic = QueryService.LOGIC.get(logic)(
                QueryService.DATETIMEPARTS.get(dtpart)(timer), arg
            )
            return _logic
        except Exception as e:
            raise Exception(f"Error in async_datepart: {e}")

    AND = "AND"
    OR = "OR"
    LOGIC = {
        DatePartModelType.Equal: lambda a, dtp: dtp == a,
        DatePartModelType.Less: lambda a, dtp: a < dtp,
        DatePartModelType.Greater: lambda a, dtp: a > dtp,
        DatePartModelType.Not: lambda a, dtp: dtp != a,
        DatePartModelType.LessOrEqual: lambda a, dtp: a <= dtp,
        DatePartModelType.GreaterOrEqual: lambda a, dtp: a >= dtp,
        DatePartModelType.In: lambda a, dtp: a in dtp,
    }
    DATETIMEPARTS = {
        DatePartDateType.Weekday: lambda d: d.weekday(),
        DatePartDateType.Month: lambda d: d.month,
        DatePartDateType.Hour: lambda d: d.hour,
    }
