WEEKDAYBITS = {
    1: 1,
    2: 2,
    3: 4,
    4: 8,
    5: 16,
    6: 32,
    0: 64
}

class WeekdayTranslation:
    @staticmethod
    def get_days(inp: int) -> list:
        _rest = inp
        ret = []
        while _rest > 0:
            val = max({k: v for k, v in WEEKDAYBITS.items() if v <= _rest}.values())
            ret.append([k for k, v in WEEKDAYBITS.items() if v == val][0])
            _rest = _rest - val
        return ret

    @staticmethod
    def set_days(input: list) -> int:
        ret = 0
        for i in input:
            ret += WEEKDAYBITS[i]
        return ret


# testdays = [1,3,5]
# schema = WeekdayTranslation.set_days(testdays)
# print(schema)
# print(WeekdayTranslation.get_days(schema))

