from datetime import datetime

def _convert_quarterly_minutes(minute:int, is_quarterly:bool) -> int:
    if is_quarterly is True:
        return (minute%15) * 4
    else:
        return minute
    
async def async_convert_quarterly_minutes(minute:int, is_quarterly:bool) -> int:
    if is_quarterly is True:
        return (minute%15) * 4
    else:
        return minute

def parse_datetime(dtstring:str) -> datetime:
    pass

def nametoid(input_string) -> str:
    return input_string.lower().replace(" ", "_").replace(",", "")

def try_parse(input_string:str, parsetype:type):
    try:
        ret = parsetype(input_string)
        return ret
    except Exception as e:
        return False