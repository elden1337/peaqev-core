from .models.hour_price import HourPrice
from ...models.hourselection.cautionhourtype import CautionHourType
from .models.hour_type import HourType


@staticmethod
def set_initial_permittance(
    hour_prices: list[HourPrice], price_mean: float, price_stdev: float
) -> None:
    for hp in hour_prices:
        if hp.hour_type == HourType.BelowMin:
            hp.permittance = 1.0
        elif hp.hour_type == HourType.AboveMax:
            hp.permittance = 0.0
        elif hp.price < price_mean - price_stdev:
            hp.permittance = 1.0
        elif hp.price > price_mean + price_stdev:
            hp.permittance = 0.0
        else:
            hp.permittance = round(
                1.0 - ((hp.price - price_mean + price_stdev) / (2 * price_stdev)), 2
            )


@staticmethod
def set_scooped_permittance(
    hour_prices: list[HourPrice], caution_hour_type: CautionHourType
) -> None:
    lo_cutoff = 0.4
    hi_cutoff = 0.75
    max_hours = 24  # todo: add support for 96 if quarterly
    match caution_hour_type:
        case CautionHourType.SUAVE:
            hi_cutoff = 0.7
        case CautionHourType.INTERMEDIATE:
            lo_cutoff = 0.5
            hi_cutoff = 0.7
        case CautionHourType.AGGRESSIVE:
            lo_cutoff = 0.6
        case CautionHourType.SCROOGE:
            lo_cutoff = 0.6
            max_hours = 8  # todo: add support for 32 if quarterly

    for i in hour_prices:
        _t = i.permittance
        if i.permittance <= lo_cutoff:
            i.permittance = 0.0
        elif i.permittance >= hi_cutoff:
            i.permittance = 1.0
        else:
            i.permittance = round(i.permittance, 2)
