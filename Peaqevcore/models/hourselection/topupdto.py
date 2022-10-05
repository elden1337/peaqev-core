from dataclasses import InitVar, dataclass, field
from .hourobject import HourObject
from .hourselectionmodels import HourSelectionModel

@dataclass
class HoursDTO:
    nh: list
    ch: list
    dyn_ch: dict
    top_price:float
    min_price:float


@dataclass
class TopUpDTO():
    """DTO-object to transfer between hourselection and top_up"""
    raw_model : HourSelectionModel
    hour:int
    hours: HoursDTO = field(init=False)
    today_hours:HourObject = field(init=False)
    tomorrow_hours:HourObject = field(init=False)
    prices: list = field(init=False)
    prices_tomorrow:list = field(init=False)
    
    def __post_init__(self):
        self.hours = HoursDTO(
            nh=self.raw_model.hours.non_hours,
            ch = self.raw_model.hours.caution_hours,
            dyn_ch = self.raw_model.hours.dynamic_caution_hours,
            top_price = self.raw_model.options.absolute_top_price,
            min_price = self.raw_model.options.min_price
        )
        self.today_hours = self.raw_model.hours.hours_today
        self.tomorrow_hours = self.raw_model.hours.hours_tomorrow
        self.prices = self.raw_model.prices_today
        self.prices_tomorrow = self.raw_model.prices_tomorrow

    