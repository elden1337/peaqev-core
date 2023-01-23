from ....services.locale.querytypes.queryservice import QueryService
from ....models.locale.enums.querytype import QueryType
from ..time_pattern import TimePattern
from ....models.locale.price import LocalePrice
from ....models.locale.enums.price_type import PriceType
from ....models.locale.enums.calendar_periods import CalendarPeriods
from ..querytypes.const import (
    QUERYTYPE_BASICMAX_MON_FRI_07_17_DEC_MAR_ELSE_REGULAR,
    QUERYTYPE_SOLLENTUNA,
    QUERYTYPE_MAX_NOV_MAR_MON_FRI_06_22,
    QUERYTYPE_AVERAGEOFTHREEHOURS_MON_FRI_07_19,
)

from ..querytypes.querysets import QUERYSETS
from ..querytypes.querytypes import QUERYTYPES
from dataclasses import dataclass
from ..locale_model import Locale_Type


@dataclass(frozen=True)
class SE_Sollentuna(Locale_Type):
    observed_peak = QueryType.AverageOfThreeHours
    charged_peak = QueryType.AverageOfThreeHours
    query_model = QUERYTYPES[QueryType.AverageOfThreeHours]
    query_model.set_query_service(QueryService(QUERYSETS[QUERYTYPE_SOLLENTUNA]))

    free_charge_pattern = TimePattern([
        {
            CalendarPeriods.Month:   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            CalendarPeriods.Weekday: [0, 1, 2, 3, 4],
            CalendarPeriods.Hour:    [19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]
        },
        {
            CalendarPeriods.Month:   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            CalendarPeriods.Weekday: [5, 6],
            CalendarPeriods.Hour:    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                                      23]
        }
    ])

    # Rörlig avgift sommar april – oktober 61,46 kr/kW
    # Rörlig avgift vinter november – mars 122,92 kr/kW
    # https://www.seom.se/el/elnat/2022-ars-priser-och-villkor/


@dataclass(frozen=True)
class SE_Skovde(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]
    query_model.set_query_service(QueryService(QUERYSETS[QUERYTYPE_MAX_NOV_MAR_MON_FRI_06_22]))

    free_charge_pattern = TimePattern([
        {
            CalendarPeriods.Month:   [11, 12, 1, 2, 3],
            CalendarPeriods.Weekday: [5, 6],
            CalendarPeriods.Hour:    [22, 23, 0, 1, 2, 3, 4, 5]
        },
        {
            CalendarPeriods.Month:   [4, 5, 6, 7, 8, 9, 10],
            CalendarPeriods.Weekday: [0, 1, 2, 3, 4, 5, 6],
            CalendarPeriods.Hour:    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                                      23]
        }
    ])

    # November-Mars, vardagar (mån-fre) 06-22
    # single peak i denna period månadsvis.


@dataclass(frozen=True)
class SE_SHE_AB(Locale_Type):
    observed_peak = QueryType.AverageOfThreeHours
    charged_peak = QueryType.AverageOfThreeHours
    query_model = QUERYTYPES[QueryType.AverageOfThreeHours]
    query_model.set_query_service(QueryService(QUERYSETS[QUERYTYPE_AVERAGEOFTHREEHOURS_MON_FRI_07_19]))

    free_charge_pattern = TimePattern([
        {
            CalendarPeriods.Month:   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            CalendarPeriods.Weekday: [5, 6],
            CalendarPeriods.Hour:    [19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]
        }
    ])

    """
    Elnätskunder med effekttaxa får vinterpris på överföringsavgift från och med 1 november – 31 mars. 
    Prishöjningen på effekttaxan skedde 1 april men blir mer kännbart när vinterpriset nu träder i kraft. 
    Kunder som bor i villa och har effekttaxa kan påverka sin kostnad genom att försöka skjuta på sådan förbrukning 
    som är möjlig från dagtid till kvällstid (19.00-07:00) eller till helger och röda dagar då det är helt kostnadsfritt att använda elnätet.
    Överföringsavgiften beräknas på medelmånadsvärdet av de tre högsta effektvärden dagtid vardagar mellan 07.00-19.00.
    
    Nov – Mars vardagar kl 7-19 135,00 kr/kW inkl moms
    April – Okt vardagar kl 7-19 56,00 kr/kW inkl moms
    """


@dataclass(frozen=True)
class SE_Partille(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]


@dataclass(frozen=True)
class SE_FalbygdensEnergi(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]


@dataclass(frozen=True)
class SE_Nacka_normal(Locale_Type):
    observed_peak = QueryType.AverageOfThreeHours
    charged_peak = QueryType.AverageOfThreeHours
    query_model = QUERYTYPES[QueryType.AverageOfThreeHours]

    # https://www.nackaenergi.se/images/downloads/natavgifter/FAQ_NYA_TARIFFER.pdf


@dataclass(frozen=True)
class SE_NACKA_timediff(Locale_Type):
    pass

    # this class is for nacka time differentiated peaks.
    # https://www.nackaenergi.se/images/downloads/natavgifter/FAQ_NYA_TARIFFER.pdf


@dataclass(frozen=True)
class SE_Malung_Salen(Locale_Type):
    observed_peak = QueryType.AverageOfFiveDays
    charged_peak = QueryType.AverageOfFiveDays
    query_model = QUERYTYPES[QueryType.AverageOfFiveDays]
    free_charge_pattern = TimePattern([
        {
            CalendarPeriods.Month:   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            CalendarPeriods.Weekday: [0, 1, 2, 3, 4, 5, 6],
            CalendarPeriods.Hour:    [19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]
        }
    ])

    # Rörlig avgift sommar april – oktober 35 kr/kW
    # Rörlig avgift vinter november – mars 118,75 kr/kW


@dataclass(frozen=True)
class SE_Linde_Energi(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]
    # docs: https://www.lindeenergi.se/elnat/elnatspriser/effekttariffer.4.1491a0b016e44ba6ccfe91b4.html

    """
    Din effektavgift baseras på din högsta effekttopp per månad, alltså den timme per månad då du använder mest el sammantaget, oavsett tid på dygnet. 
    Under perioden november till mars tillkommer en högbelastningslastavgift, så kallad höglasteffekt, då du även debiteras för ditt högst uppmätta timvärde vardagar kl 07:00-19:00.
    Under vintermånaderna kan du alltså debiteras för två olika timvärden, beroende på när på dygnet din effekttopp uppmäts.
    """


@dataclass(frozen=True)
class SE_Kristinehamn(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]
    query_model.set_query_service(QueryService(QUERYSETS[QUERYTYPE_BASICMAX_MON_FRI_07_17_DEC_MAR_ELSE_REGULAR]))

    """
    https://kristinehamnsenergi.se/elnat/elnatsavgiften/effektavgift-villa-med-bergvarmepump/
    vardagar november-mars, kl 07.00-17.00 > highload instead of normal load. other times, normal load
    """


@dataclass(frozen=True)
class SE_Karlstad(Locale_Type):
    observed_peak = QueryType.Max  # todo check if correct
    charged_peak = QueryType.Max  # todo check if correct
    query_model = QUERYTYPES[QueryType.Max]
    # docs: https://karlstadsnat.se/elnat/kund/priser-och-tariffer/effekttariff/
    """
    Note, high load extra is added on weekdays from 6-18 during november - march. 
    This does not affect the peak, but should in future updates be cause for forced non-/or caution-hours to lessen the cost for the consumer.
    """


@dataclass(frozen=True)
class SE_Gothenburg(Locale_Type):
    observed_peak = QueryType.AverageOfThreeDays
    charged_peak = QueryType.AverageOfThreeDays
    query_model = QUERYTYPES[QueryType.AverageOfThreeDays]
    price = LocalePrice(
        price_type=PriceType.Static,
        value=36.25,
        currency="SEK"
    )


@dataclass(frozen=True)
class SE_Bjerke_Energi(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]
    price = LocalePrice(
        price_type=PriceType.Seasoned,
        currency="SEK"
        value=
    )
    free_charge_pattern = TimePattern([
        {
            CalendarPeriods.Month:   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            CalendarPeriods.Weekday: [0, 1, 2, 3, 4, 5, 6],
            CalendarPeriods.Hour:    [22, 23, 0, 1, 2, 3, 4, 5]
        }
    ])

    # docs: https://www.bjerke-energi.se/elnat/tariffer/effekttariff-fr-o-m-2022-02-01/
    # dag kl. 06-22 nov-mars                 106,25 kr/kW/mån
    # dag kl. 06-22 april-okt                50 kr/kW/mån
    # natt kl. 22-06 alla dagar hela året    0 kr/kW/mån
    """
    Note, high load extra is added from 06-22 during november - march. 
    This does not affect the peak, but should in future 
    """


@dataclass(frozen=True)
class SE_Telge_Energi(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]
    free_charge_pattern = TimePattern([
        {
            CalendarPeriods.Month:   [4, 5, 6, 7, 8, 9, 10],
            CalendarPeriods.Weekday: [0, 1, 2, 3, 4, 5, 6],
            CalendarPeriods.Hour:    [21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                      20]
        }
        ,
        {
            CalendarPeriods.Month:   [11, 12, 1, 2, 3],
            CalendarPeriods.Weekday: [5, 6],
            CalendarPeriods.Hour:    [21, 22, 23, 0, 1, 2, 3, 4, 5, 6]
        }
    ]
    )

    # docs: https://nya.telge.se/elnat/ny-prismodell-elnat/om-hog--och-laglasttid/

    """
    Det högre priset gäller bara på helgfria vardagar 07.00-20.00 under november till mars.
    """


@dataclass(frozen=True)
class SE_Malarenergi(Locale_Type):
    observed_peak = QueryType.AverageOfThreeHours
    charged_peak = QueryType.AverageOfThreeHours
    query_model = QUERYTYPES[QueryType.AverageOfThreeHours]

    # docs: https://www.malarenergi.se/el/elnat/effekttariffer/

    """
    Det högre priset gäller bara på helgfria vardagar 07.00-20.00 under november till mars.
    """


@dataclass(frozen=True)
class SE_TekniskaVerken_Link(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]

    # docs: unknown


@dataclass(frozen=True)
class SE_Eskilstuna(Locale_Type):
    observed_peak = QueryType.Max
    charged_peak = QueryType.Max
    query_model = QUERYTYPES[QueryType.Max]

    # docs: unknown
