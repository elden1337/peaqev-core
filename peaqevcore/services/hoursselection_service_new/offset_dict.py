from datetime import date, timedelta
from .const import TODAY, TOMORROW
from statistics import mean, stdev


def get_offset_dict(offset_dict) -> dict:
    vals = offset_dict.keys()
    if len(vals) == 1:
        return {TODAY: offset_dict.values(), TOMORROW: {}}
    elif len(vals) == 2:
        return {
            TODAY: offset_dict[min(vals)],
            TOMORROW: offset_dict[max(vals)],
        }
    # todo: log something here.
    return {
        TODAY: {},
        TOMORROW: {},
    }


def set_offset_dict(prices: list[float], day: date) -> dict:
    ret = {}
    _len = len(prices)
    today: list = []
    tomorrow: list = []
    match _len:
        case 23 | 24 | 25 | 92 | 96 | 100:
            today = prices
        case 47 | 48 | 49 | 188 | 192 | 196:
            today = prices[: len(prices) // 2]
            tomorrow = prices[len(prices) // 2 : :]
            print(f"today: {today}")
            print(f"tomorrow: {tomorrow}")
    ret[day] = _deviation_from_mean(today, today)
    ret[day + timedelta(days=1)] = _deviation_from_mean(tomorrow, prices)
    # todo: handle interim
    return ret


def _deviation_from_mean(prices: list[float], checker: list[float]) -> dict[int, float]:
    if not len(prices):
        return {}
    avg = mean(checker)
    devi = stdev(prices)
    deviation_dict = {}
    for i, num in enumerate(prices):
        deviation = (num - avg) / devi
        if devi < 1:
            deviation *= 0.5
        deviation_dict[i] = round(deviation, 2)
    return deviation_dict
