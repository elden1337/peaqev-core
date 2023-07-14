import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


async def async_create_dict(input: list):
    ret = {}
    for idx, val in enumerate(input):
        ret[idx] = val
    if 23 <= len(ret) <= 24:
        return ret
    elif len(ret) == 25:
        _LOGGER.debug(f"Looks like we are heading into DST. re-parsing hours")
        input.pop(2)
        return await async_create_dict(input)
    else:
        _LOGGER.exception(
            f"Could not create dictionary from pricelist: {input} with len {len(ret)}."
        )
        raise ValueError


def convert_none_list(lst: Any) -> list:
    ret = []
    if lst is None or not isinstance(lst, list):
        return ret
    try:
        for l in lst:
            if l is None:
                return ret
            elif not _try_parse(l, float):
                return ret
        return lst
    except:
        return _make_array_from_empty(str(lst))


def _try_parse(input: str, parsetype: type):
    try:
        ret = parsetype(input)
        return ret
    except:
        return False


def _make_array_from_empty(input: str) -> list:
    array = input.split(",")
    list = [p for p in array if len(p)]
    ret = []
    if len(list) > 24:
        try:
            for l in list:
                parsed_item = _try_parse(l, float)
                if not parsed_item:
                    parsed_item = _try_parse(l, int)
                assert isinstance(parsed_item, (float, int))
                ret.append(parsed_item)
            return ret
        except:
            _LOGGER.warning("Unable to create empty list for prices.")
            pass
    return []

