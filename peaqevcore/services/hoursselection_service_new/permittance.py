from .models.hour_price import HourPrice
from ...common.enums.cautionhourtype import CautionHourType
from .models.hour_type import HourType
from statistics import mean, stdev

LOCUTOFF = "lo_cutoff"
HICUTOFF = "hi_cutoff"
MAXHOURS = "max_hours"
MINHOURS = "min_hours"

def set_blank_permittance(hour_prices: list[HourPrice]) -> None:
    for hour in hour_prices:
        if hour.hour_type != HourType.AboveMax:
            hour.permittance = 1.0

def set_initial_permittance(
    hours: list[HourPrice],
    avg7: float | None = None,
    non_hours: list[int] = []
) -> None:
    avg = mean([h.price for h in hours if not h.passed])
    ceil = mean([avg, avg7]) if avg7 is not None else avg
    floor = min(avg, avg7) if avg7 is not None else 0
    for hour in hours:
        if not hour.passed:
            if hour.dt.hour in non_hours:
                hour.permittance = 0.0
            elif hour.price < floor:
                hour.permittance = 1.0
            elif hour.price > ceil:
                hour.permittance = 0.0
            else:
                hour.permittance = (hour.price < ceil) * (0.2 + 0.8 * (ceil - hour.price) / (ceil - floor))


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
    available_len = 0
    _min_hours = opt.get(MINHOURS, 4)
    available_len = len(
        [hp for hp in hour_prices if hp.permittance == 1 and not hp.passed]
    )
    if available_len < _min_hours:
        selectable_hours = [
            hp
            for hp in hour_prices
            if hp.hour_type != HourType.AboveMax
            and not hp.passed
            and hp.permittance < 1
        ]
        if len(selectable_hours):
            selectable_hours.sort(key=lambda x: (x.price,x.dt))
            min_selected = selectable_hours[0]
            for h in range(0,int(_min_hours - available_len)):
                selectable_hours[h].permittance = 1.0
            for select in selectable_hours:
                if select.price / min_selected.price < 1.1:
                    select.permittance = 1.0

    discard_peaks(hour_prices)

def _get_caution_options(caution_hour_type: CautionHourType, is_quarterly:bool = False) -> dict[str,float]:
    _quarters = 4 if is_quarterly else 1
    lo_cutoff = 0.5
    hi_cutoff = 0.8
    max_hours = 24 *_quarters
    min_hours = 4
    match caution_hour_type:
        case CautionHourType.SUAVE:
            lo_cutoff = 0.2
            hi_cutoff = 0.5
        case CautionHourType.INTERMEDIATE:
            lo_cutoff = 0.45
            hi_cutoff = 0.65
        case CautionHourType.AGGRESSIVE:
            lo_cutoff = 0.55
            max_hours = 20 * _quarters
        case CautionHourType.SCROOGE:
            lo_cutoff = 0.55
            max_hours = 8 * _quarters
            min_hours = 0
    return {
        LOCUTOFF: lo_cutoff,
        HICUTOFF: hi_cutoff,
        MAXHOURS: max_hours,
        MINHOURS: min_hours,
    }

def discard_peaks(hour_prices: list[HourPrice]) -> None:
    if _is_pointy(hour_prices):
        _set_peak_permittance_adjacent(hour_prices)
    else:
        _set_peak_permittance(hour_prices)

def _set_peak_permittance(hour_prices: list[HourPrice], threshold: float = 0.05) -> None:
    for i in range(1, len(hour_prices) - 1):
        prev_price = hour_prices[i-1].price
        current_price = hour_prices[i].price
        next_price = hour_prices[i+1].price
        if current_price > prev_price * (1 + threshold) and current_price > next_price * (1 + threshold):
            if hour_prices[i].hour_type != HourType.BelowMin:
                hour_prices[i].permittance = 0.0

def _set_peak_permittance_adjacent(hour_prices: list[HourPrice]) -> None:
    prices = [hour.price for hour in hour_prices]
    std_dev = stdev(prices)
    for i in range(1, len(hour_prices) - 1):
        if hour_prices[i].price > hour_prices[i-1].price and hour_prices[i].price > hour_prices[i+1].price:
            if hour_prices[i].price - hour_prices[i-1].price > std_dev and hour_prices[i].price - hour_prices[i+1].price > std_dev:
                if hour_prices[i].hour_type != HourType.BelowMin:
                    hour_prices[i].permittance = 0.0 
                if hour_prices[i-1].hour_type != HourType.BelowMin:
                    hour_prices[i-1].permittance = 0.0
                if hour_prices[i+1].hour_type != HourType.BelowMin:
                    hour_prices[i+1].permittance = 0.0

def _is_pointy(hour_prices:list[HourPrice]) -> bool:
    _prices = [hp.price for hp in hour_prices]
    return mean(_prices) < max(_prices) - min(_prices)