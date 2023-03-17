import statistics as stat
import logging
from ....models.hourselection.hourobject import HourObject
from ....models.hourselection.cautionhourtype import CautionHourType

_LOGGER = logging.getLogger(__name__)


ALLOWANCE_SCHEMA = {
    CautionHourType.get_num_value(CautionHourType.SUAVE): 1.15,
    CautionHourType.get_num_value(CautionHourType.INTERMEDIATE): 1.05,
    CautionHourType.get_num_value(CautionHourType.AGGRESSIVE): 1,
    CautionHourType.get_num_value(CautionHourType.SCROOGE): 1
}

def create_dict(input: list):
    ret = {}
    for idx, val in enumerate(input):
        ret[idx] = val
    if 23 <= len(ret) <= 24:
        return ret
    elif len(ret) == 25:
        _LOGGER.debug(f"Looks like we are heading into DST. re-parsing hours")
        input.pop(2)
        return create_dict(input)
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

def convert_collections(new: HourObject, index_deviation: int) -> HourObject:
    """Converts the hourobject-collections to interim days, based on the index-deviation provided."""
    def _chop_list(lst: list):
        return [n+index_deviation for n in lst if 0 <= n+index_deviation < 24]
    def _chop_dict(dct: dict):
        return {key+index_deviation:value for (key,value) in dct.items() if 0 <= key+index_deviation < 24}
    ret = HourObject([], [], {})
    ret.nh = _chop_list(new.nh)
    ret.ch = _chop_list(new.ch)
    ret.dyn_ch = _chop_dict(new.dyn_ch)
    ret.offset_dict = _chop_dict(new.offset_dict)
    ret.pricedict = _chop_dict(new.pricedict)
    return ret

    
def try_remove(value, collection: list|dict):
    if isinstance(collection, dict):
        if value in collection.keys():
            collection.pop(value)
    elif isinstance(collection, list):
        if value in collection:
            collection.remove(value)
    return collection