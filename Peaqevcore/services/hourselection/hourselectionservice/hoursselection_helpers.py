import statistics as stat
import logging
from ....models.hourselection.hourobjects.hourobject import HourObject


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
        _LOGGER.exception(f"Could not create dictionary from pricelist: {input} with len {len(ret)}.")
        raise ValueError


def convert_none_list(lst: any) -> list:
    ret = []
    if lst is None or not isinstance(lst, list):
        return ret
    try:
        for l in lst:
            if l is None:
                return ret
        return lst
    except:
        return _make_array_from_empty(lst)


def _try_parse(input:str, parsetype:type):
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
                assert isinstance(parsed_item, (float,int))
                ret.append(parsed_item)
            return ret
        except:
            _LOGGER.warning("Unable to create empty list for prices.")
            pass
    return []
    
async def async_try_remove(value, collection: list|dict):
    if isinstance(collection, dict):
        if value in collection.keys():
            collection.pop(value)
    elif isinstance(collection, list):
        if value in collection:
            collection.remove(value)
    return collection