import logging
from ...models.hourselection.cautionhourtype import CautionHourType
from ...models.hourselection.hourselectionmodels import HourSelectionModel, HourSelectionOptions
from ...models.hourselection.hourtypelist import HourTypeList
from .hourselectionservice.hourselectionservice import HourSelectionService
from .hourselectionservice.hoursselection_helpers import convert_none_list
_LOGGER = logging.getLogger(__name__)


class Hoursselection:
    def __init__(
            self,      
            absolute_top_price: float = 0,
            min_price: float = 0,
            cautionhour_type: str = CautionHourType.SUAVE.value,
            blocknocturnal: bool = False,
            base_mock_hour: int = None
    ):
        self.cautionhour_type_enum = CautionHourType(cautionhour_type.lower()) if isinstance(cautionhour_type, str) else cautionhour_type
        self.model = HourSelectionModel(
            options=HourSelectionOptions(
                cautionhour_type=CautionHourType.get_num_value(cautionhour_type), 
                min_price=min_price,
                top_price= absolute_top_price,
                blocknocturnal= blocknocturnal
                    )
                )
        self.model.validate()
        self.service = HourSelectionService(parent=self, base_mock_hour=base_mock_hour)
    
    @property
    def offsets(self) -> dict:
        return self.model.hours.offset_dict

    @property
    def non_hours(self) -> list:
        self.service.update_hour_lists(listtype=HourTypeList.NonHour)
        return self.model.hours.non_hours

    @property
    def caution_hours(self) -> list:
        self.service.update_hour_lists(listtype=HourTypeList.CautionHour)
        return self.model.hours.caution_hours

    @property
    def dynamic_caution_hours(self) -> dict:
        self.service.update_hour_lists(listtype=HourTypeList.DynCautionHour)
        return self.model.hours.dynamic_caution_hours

    @property
    def prices(self) -> list:
        return self.model.prices_today

    @prices.setter
    def prices(self, val):
        self.model.prices_today = val
        if self.prices == self.prices_tomorrow:
            self.prices_tomorrow = []
        else:
            self.update(caller="today")

    @property
    def prices_tomorrow(self) -> list:
        return self.model.prices_tomorrow

    @prices_tomorrow.setter
    def prices_tomorrow(self, val):
        self.model.prices_tomorrow = convert_none_list(val)
        if self.model.prices_tomorrow != []:
            self.service._preserve_interim = False
        self.update()

    @property
    def adjusted_average(self):
        return self.model.adjusted_average

    @adjusted_average.setter
    def adjusted_average(self, val):
        self.model.adjusted_average = val

    def update_top_price(self, dyn_top_price) -> None: 
        self.model.options.set_absolute_top_price(
            min(
            dyn_top_price,
            self.model.options.absolute_top_price
            ), 
            self.model.options.min_price
            )
        self.update()

    def update(self, testhour:int = None, caller:str = None) -> None:
        if testhour is not None:
            self.service._mock_hour = testhour
        self.service.update(caller)

    def get_average_kwh_price(self):
        ret = self._get_charge_or_price()
        try:
            return round(sum(ret.values())/len(ret),2)
        except ZeroDivisionError as e:
                _LOGGER.warning(f"get_average_kwh_price_core could not be calculated: {e}")
        return 0
        
    def get_total_charge(self, currentpeak:float) -> float:
        self.model.current_peak = currentpeak
        ret = self._get_charge_or_price(True)
        return round(sum(ret.values()),1)

    def _get_charge_or_price(self, charge:bool = False) -> dict:
        hour = self.service.set_hour()
        ret = {}

        def _looper_charge(h:int):
            if h in self.model.hours.dynamic_caution_hours:
                    ret[h] = self.model.hours.dynamic_caution_hours[h] * self.model.current_peak
            elif h in self.model.hours.non_hours:
                ret[h] = 0
            else:
                ret[h] = self.model.current_peak

        def _looper_price(h:int, tomorrow_active:bool):
            if h in self.model.hours.dynamic_caution_hours:
                    if tomorrow_active:
                        if h < hour and len(self.prices_tomorrow):
                            ret[h] = self.model.hours.dynamic_caution_hours[h] * self.prices_tomorrow[h]
                    if h >= hour:
                        ret[h] = self.model.hours.dynamic_caution_hours[h] * self.prices[h]
            elif h not in self.model.hours.non_hours:
                if h < hour and len(self.prices_tomorrow):
                    ret[h] = self.prices_tomorrow[h]
                if h >= hour:
                    ret[h] = self.prices[h]

        if self.prices_tomorrow is None or len(self.prices_tomorrow) < 1:
            for h in range(hour,24):
                if charge:
                    _looper_charge(h)
                else:
                    _looper_price(h, False)
        else:
            for h in range(hour,(hour+24)):
                h = h-24 if h > 23 else h
                if charge:
                    _looper_charge(h)
                else:
                    _looper_price(h, True)
        return ret

