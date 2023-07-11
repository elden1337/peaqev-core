from .models.hour_price import HourPrice
from ...models.hourselection.cautionhourtype import CautionHourType
from .models.hour_type import HourType
from statistics import mean, stdev

LOCUTOFF = "lo_cutoff"
HICUTOFF = "hi_cutoff"
MAXHOURS = "max_hours"
MINHOURS = "min_hours"


def _set_max_permittance(hour_price: HourPrice,average:float, avg7: float|None) -> float:
    return 1.0


def _set_min_permittance(hour_price: HourPrice,average:float, avg7: float|None) -> float:
    return 0.0


def _calculate_score(hour: HourPrice, average:float, avg7: float|None) -> float:
    if avg7 is None:
        return 1.0 if hour.price < average else 0.0
    else:
        ceil = max(average, avg7)
        floor = min(average, avg7)
        return round(0.4 + 0.6 * (ceil - hour.price) / (ceil - floor),2)


HOURTYPECONVERSION = {
    HourType.BelowMin: _set_max_permittance,
    HourType.AboveMax: _set_min_permittance,
    HourType.Regular: _calculate_score
}


def set_initial_permittance(
    hours: list[HourPrice],
    avg7: float | None = None,
) -> None:
    for hour in hours:
        hour.permittance = HOURTYPECONVERSION[hour.hour_type](hour, average=mean([h.price for h in hours if not h.passed]), avg7 = avg7)


def set_scooped_permittance(
    hour_prices: list[HourPrice], caution_hour_type: CautionHourType
) -> None:
    opt = _get_caution_options(caution_hour_type)
    for hp in hour_prices:
        if hp.permittance <= opt.get(LOCUTOFF, 0.4):
            hp.permittance = 0.0
        elif hp.permittance >= opt.get(HICUTOFF, 0.75):
            hp.permittance = 1.0
        else:
            hp.permittance = round(hp.permittance, 2)


def set_min_allowed_hours(
    hour_prices: list[HourPrice], caution_hour_type: CautionHourType
) -> None:
    opt = _get_caution_options(caution_hour_type)
    available_len = len(
        [hp for hp in hour_prices if hp.permittance == 1 and not hp.passed]
    )
    if available_len < opt.get(MINHOURS, 4):
        _t = [
            hp
            for hp in hour_prices
            if hp.list_type != HourType.AboveMax
            and not hp.passed
            and hp.permittance < 1
        ]
        if len(_t):
            _t.sort(key=lambda x: x.price)
            for h in range((opt.get(MINHOURS, 4) - available_len)):
                _t[h].permittance = 1.0


def _get_caution_options(caution_hour_type: CautionHourType) -> dict:
    lo_cutoff = 0.4
    hi_cutoff = 0.75
    max_hours = 24  # todo: add support for 96 if quarterly
    min_hours = 4
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
            min_hours = 0
    return {
        LOCUTOFF: lo_cutoff,
        HICUTOFF: hi_cutoff,
        MAXHOURS: max_hours,
        MINHOURS: min_hours,
    }
