from ....models.locale.queryservice_model import QueryServiceModel, Group, DatePartModel
from ....models.locale.enums.datepart_datetype import DatePartDateType
from ....models.locale.enums.datepart_modeltype import DatePartModelType
from .const import (
    QUERYTYPE_AVERAGEOFTHREEHOURS_MON_FRI_07_19,
    QUERYTYPE_HIGHLOAD,
    QUERYTYPE_MAX_NOV_MAR_MON_FRI_06_22,
    QUERYTYPE_SOLLENTUNA,
    QUERYTYPE_BASICMAX_MON_FRI_07_17_DEC_MAR_ELSE_REGULAR,
    QUERYTYPE_NEVER
    )
from .queryservice import Dividents

QUERYSETS = {
    QUERYTYPE_NEVER: QueryServiceModel(
    [Group(divident=Dividents.AND, dateparts=[
        DatePartModel(type=DatePartModelType.GreaterOrEqual, dttype=DatePartDateType.Hour, values=[24])
        ])
    ]
    ),
    QUERYTYPE_SOLLENTUNA: QueryServiceModel(
    [Group(divident=Dividents.AND, dateparts=[
        DatePartModel(type=DatePartModelType.GreaterOrEqual, dttype=DatePartDateType.Hour, values=[7]),
        DatePartModel(type=DatePartModelType.LessOrEqual, dttype=DatePartDateType.Hour, values=[18]),
        DatePartModel(type=DatePartModelType.LessOrEqual, dttype=DatePartDateType.Weekday, values=[4])
        ]
        )
    ]
    ),
    QUERYTYPE_MAX_NOV_MAR_MON_FRI_06_22: QueryServiceModel(
    [Group(divident=Dividents.AND, dateparts=[
            DatePartModel(type=DatePartModelType.GreaterOrEqual, dttype=DatePartDateType.Hour, values=[6]),
            DatePartModel(type=DatePartModelType.LessOrEqual, dttype=DatePartDateType.Hour, values=[22]),
            DatePartModel(type=DatePartModelType.LessOrEqual, dttype=DatePartDateType.Weekday, values=[4]),
            DatePartModel(type=DatePartModelType.In, dttype=DatePartDateType.Month, values=[11, 12, 1, 2, 3])
        ]
        )
    ]
    ),
    QUERYTYPE_AVERAGEOFTHREEHOURS_MON_FRI_07_19: QueryServiceModel(
        [Group(divident=Dividents.AND, dateparts=[
            DatePartModel(type=DatePartModelType.In, dttype=DatePartDateType.Hour, values=[7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]),
            DatePartModel(type=DatePartModelType.LessOrEqual, dttype=DatePartDateType.Weekday, values=[4])
        ]
        )
    ]
    ),
    QUERYTYPE_BASICMAX_MON_FRI_07_17_DEC_MAR_ELSE_REGULAR: QueryServiceModel(
        [Group(divident=Dividents.AND, dateparts=[
            DatePartModel(type=DatePartModelType.In, dttype=DatePartDateType.Hour, values=[7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
            DatePartModel(type=DatePartModelType.LessOrEqual, dttype=DatePartDateType.Weekday, values=[4]),
            DatePartModel(type=DatePartModelType.In, dttype=DatePartDateType.Month, values=[12, 1, 2, 3])
        ]
        ),
        Group(divident=Dividents.OR, dateparts=[
            DatePartModel(type=DatePartModelType.In, dttype=DatePartDateType.Month, values=[4, 5, 6, 7, 8, 9, 10, 11])
            ])
    ]
    ),
    QUERYTYPE_HIGHLOAD: QueryServiceModel(
        [Group(divident=Dividents.AND, dateparts=[
            DatePartModel(type=DatePartModelType.In, dttype=DatePartDateType.Hour, values=[8, 9, 10, 11, 12, 13, 14, 15, 16,17,18]),
            DatePartModel(type=DatePartModelType.LessOrEqual, dttype=DatePartDateType.Weekday, values=[4])
        ]
        )
    ]
    )
}