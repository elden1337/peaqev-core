from .models.hour_price import HourPrice
from ...models.hourselection.cautionhourtype import CautionHourType
from .models.hour_type import HourType
from statistics import mean

LOCUTOFF = "lo_cutoff"
HICUTOFF = "hi_cutoff"
MAXHOURS = "max_hours"
MINHOURS = "min_hours"

def set_initial_permittance(
    hours: list[HourPrice],
    avg7: float | None = None,
) -> None:
    avg = mean([h.price for h in hours if not h.passed])
    ceil = max(avg, avg7) if avg7 is not None else avg
    floor = min(avg, avg7) if avg7 is not None else None
    get_perm = lambda hour: (hour.price < ceil) * (0.3 + 0.7 * (ceil - hour.price) / (ceil - floor)) + (hour.price >= ceil) * 0.0 + (floor is not None) * (hour.price <= floor) * 1.0
    for hour in hours:
        hour.permittance = get_perm(hour)


def set_scooped_permittance(
    hour_prices: list[HourPrice], caution_hour_type: CautionHourType
) -> None:
    opt = _get_caution_options(caution_hour_type)
    for hp in hour_prices:
        if not hp.passed:
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
            if hp.hour_type != HourType.AboveMax
            and not hp.passed
            and hp.permittance < 1
        ]
        if len(_t):
            _t.sort(key=lambda x: x.price)
            for h in range((opt.get(MINHOURS, 4) - available_len)):
                _t[h].permittance = 1.0


def _get_caution_options(caution_hour_type: CautionHourType, is_quarterly:bool = False) -> dict[str,float]:
    _quarters = 4 if is_quarterly else 1
    lo_cutoff = 0.5
    hi_cutoff = 0.8
    max_hours = 24 *_quarters
    min_hours = 4
    match caution_hour_type:
        case CautionHourType.SUAVE:
            hi_cutoff = 0.7
        case CautionHourType.INTERMEDIATE:
            lo_cutoff = 0.55
            hi_cutoff = 0.7
        case CautionHourType.AGGRESSIVE:
            lo_cutoff = 0.65
        case CautionHourType.SCROOGE:
            lo_cutoff = 0.65
            max_hours = 8 * _quarters
            min_hours = 0
    return {
        LOCUTOFF: lo_cutoff,
        HICUTOFF: hi_cutoff,
        MAXHOURS: max_hours,
        MINHOURS: min_hours,
    }
