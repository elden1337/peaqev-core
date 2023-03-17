from ....services.hourselection.hourselectionservice.hoursselection_helpers import try_remove
from .hourobject import HourObject

def update_interim_lists(_range: range, old: HourObject, new, index_devidation: int):
        _new = convert_collections(new, index_devidation)
        try:
            for i in _range:
                if i in _new.nh:
                    if i not in old.nh:
                        old.nh.append(i)
                        old.ch = try_remove(i, old.ch)
                        old.dyn_ch = try_remove(i, old.dyn_ch)
                elif i in _new.ch:
                    if i not in old.ch:
                        old.ch.append(i)
                        old.dyn_ch[i] = _new.dyn_ch[i]
                        old.nh = try_remove(i, old.nh)
                else:
                    old.nh = try_remove(i, old.nh)
                    old.ch = try_remove(i, old.ch)
                    old.dyn_ch = try_remove(i, old.dyn_ch)
                old.nh.sort()
                old.ch.sort()
                old.dyn_ch = dict(sorted(old.dyn_ch.items()))
        except IndexError:
            raise IndexError("Error on updating interim lists.")
        
        for r in _new.offset_dict.keys():
            old.offset_dict[r] = _new.offset_dict[r]
            old.pricedict[r] = _new.pricedict[r]
        return old
    
    
def convert_collections(new: HourObject, index_deviation: int) -> HourObject:
    """Converts the hourobject-collections to interim days, based on the index-deviation provided."""
    ret = HourObject([], [], {})
    ret.nh = _chop_list(new.nh, index_deviation)
    ret.ch = _chop_list(new.ch, index_deviation)
    ret.dyn_ch = _chop_dict(new.dyn_ch, index_deviation)
    ret.offset_dict = _chop_dict(new.offset_dict, index_deviation)
    ret.pricedict = _chop_dict(new.pricedict, index_deviation)
    return ret


def _chop_list(lst: list, index_deviation:int):
        return [n+index_deviation for n in lst if 0 <= n+index_deviation < 24]

def _chop_dict(dct: dict, index_deviation: int):
    return {key+index_deviation:value for (key,value) in dct.items() if 0 <= key+index_deviation < 24}
