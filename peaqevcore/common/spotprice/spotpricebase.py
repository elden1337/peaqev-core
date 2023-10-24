import logging
from abc import abstractmethod
from datetime import date, datetime
from statistics import mean
from peaqevcore.common.spotprice.const import AVERAGE_MAX_LEN
from peaqevcore.common.models.observer_types import ObserverTypes
from peaqevcore.common.spotprice.dynamic_top_price import DynamicTopPrice
from peaqevcore.common.spotprice.models.spotprice_dto import ISpotPriceDTO
from peaqevcore.common.spotprice.models.spotprice_model import SpotPriceModel
from peaqevcore.common.models.peaq_system import PeaqSystem

_LOGGER = logging.getLogger(__name__)


class MockObserver:
    async def async_broadcast(self, type: ObserverTypes, data = None) -> None:
        pass



# class SpotPriceBaseExtras:
#     def __init__(self):
#         self._dynamic_top_price = DynamicTopPrice()

#     @property
#     def average_month(self) -> float:
#         return self.model.average_month

#     @property
#     def average_three_days(self) -> float:
#         return self.model.average_three_days

#     @property
#     def average_weekly(self) -> float:
#         return self.model.average_weekly

#     @property
#     def average_30(self) -> float:
#         return self.model.average_30

#     @property
#     def average_data(self) -> dict[date, float]:
#         return self.model.average_data

#     async def async_update_dynamic_max_price(self):
#         if len(self.model.average_data) > 3:
#             _dynamic_max_price = await self._dynamic_top_price.async_get_max(
#                 list(self.model.average_data.values())
#             )
#             if self.model.dynamic_top_price != _dynamic_max_price[0]:
#                 self.model.dynamic_top_price_type = _dynamic_max_price[1].value
#                 self.model.dynamic_top_price = _dynamic_max_price[0]
#                 await self.observer.async_broadcast(
#                     ObserverTypes.DynamicMaxPriceChanged, _dynamic_max_price[0]
#                 )

#     async def async_update_average_month(self) -> None:
#         _new = self._get_average(datetime.now().day)
#         if (
#             len(self.model.average_data) >= int(datetime.now().day)
#             and self.model.average_month != _new
#         ):
#             self.model.average_month = _new
#             if self.model.average_month is not None:
#                 _LOGGER.debug(f"broadcasting average month: {_new}")
#                 await self.observer.async_broadcast(
#                     ObserverTypes.MonthlyAveragePriceChanged, _new
#                 )

#     async def async_update_average(self, length: list[int]) -> None:
#         averages_dict = {
#             3: "average_three_days",
#             7: "average_weekly",
#             30: "average_30",
#         }
#         for l in length:
#             _new = self._get_average(l)
#             if len(self.model.average_data) >= l and getattr(self.model, averages_dict[l]) != _new:
#                 setattr(self.model, averages_dict[l], _new)
#                 _LOGGER.debug(f"average {str(l)} updated to {_new}")
#         await self.async_update_adjusted_average()

#     async def async_update_adjusted_average(self) -> None:
#         adj_avg: float|None = None
#         if len(self.model.average_data) >= 7:
#             adj_avg = max(self.model.average_weekly, self.model.average_three_days)
#         elif len(self.model.average_data) >= 3:
#             adj_avg = self.model.average_three_days
#         if self.model.adjusted_average != adj_avg and adj_avg is not None:
#             self.model.adjusted_average = adj_avg
#             await self.observer.async_broadcast(
#                 ObserverTypes.AdjustedAveragePriceChanged, adj_avg
#             )

#     async def async_update_average_day(self, average) -> None:
#         if average != self.model.daily_average:
#             self.model.daily_average = average
#             await self.async_add_average_data(average)
#             await self.observer.async_broadcast(
#                 ObserverTypes.DailyAveragePriceChanged, average
#             )

#     async def async_import_average_data(self, incoming: list|dict):
#         if len(incoming):
#             self.model.create_date_dict(incoming)
#         await self.async_cap_average_data_length()
#         await self.async_update_spotprice()

#     async def async_add_average_data(self, new_val):
#         if isinstance(new_val, float):
#             rounded = round(new_val, 3)
#             if datetime.now().date not in self.model.average_data.keys():
#                 self.model.average_data[date.today()] = rounded
#             await self.async_cap_average_data_length()

#     async def async_cap_average_data_length(self):
#         while len(self.model.average_data) > AVERAGE_MAX_LEN:
#             min_key = min(self.model.average_data.keys())
#             del self.model.average_data[min_key]

#     def _get_average(self, days: int) -> float:
#         try:
#             if len(self.model.average_data) > days:
#                 avg_values = list(self.model.average_data.values())
#                 ret = avg_values[-days:]
#             elif len(self.model.average_data) == 0:
#                 return 0
#             else:
#                 ret = list(self.model.average_data.values())
#             return round(mean(ret), 2)
#         except Exception as e:
#             _LOGGER.debug(
#                 f"Could not calculate average. indata: {list(self.model.average_data.values())}, error: {e}"
#             )
#             return 0


class SpotPriceBase:
    def __init__(self, hub, source: str, system: PeaqSystem, observer = MockObserver(), test:bool = False, is_active: bool = True):
        _LOGGER.debug(f"Initializing Spotprice for {source} from system {system.value}.")
        self.hub = hub
        self.observer = observer
        self.model = SpotPriceModel(source=source)
        self._dynamic_top_price = DynamicTopPrice()
        self._is_initialized: bool = False
        #self.extras = SpotPriceBaseExtras() if system in [PeaqSystem.PeaqEv] else None
        #self.averages = SpotPriceBaseAverages() if system in [PeaqSystem.PeaqEv, PeaqSystem.PeaqHvac] else None

        self.converted_average_data: bool = False #remove this five versions from peaqev 3.2.0
        if not test:
            self.state_machine = hub.state_machine
            if is_active:
                self.setup()

    @property
    def tomorrow_valid(self) -> bool:
        return getattr(self.model, "tomorrow_valid", False)

    @property
    def entity(self) -> str:
        return getattr(self.model, "entity", "")

    @property
    def is_initialized(self) -> bool:
        return self._is_initialized

    @property
    def currency(self) -> str:
        return self.model.currency

    @property
    def state(self) -> float:
        return self.model.state

    @state.setter
    def state(self, val) -> None:
        if self.model.state != val:
            self.model.state = val

    @property
    def use_cent(self) -> bool:
        return self.model.use_cent

    @property
    def source(self) -> str:
        return self.model.source

    #not for peaqnext
    @property
    def average_month(self) -> float:
        return self.model.average_month

    #not for peaqnext
    @property
    def average_three_days(self) -> float:
        return self.model.average_three_days

    #not for peaqnext
    @property
    def average_weekly(self) -> float:
        return self.model.average_weekly

    #not for peaqnext
    @property
    def average_30(self) -> float:
        return self.model.average_30

    #not for peaqnext
    @property
    def average_data(self) -> dict[date, float]:
        return self.model.average_data


    @abstractmethod
    async def async_set_dto(self, ret, initial: bool) -> None:
        pass

    @abstractmethod
    def setup(self):
        pass

    async def async_update_spotprice(self, initial: bool = False) -> None:
        if self.entity is not None:
            ret = self.state_machine.states.get(self.entity)
            if ret is not None:
                await self.async_set_dto(ret, initial)
            else:
                _LOGGER.debug(
                    f"Could not get spot-prices. Entity: {self.entity}. Retrying..."
                )

    async def async_update_set_prices(self, result: ISpotPriceDTO) -> bool:
        ret = False
        today = await self.model.fix_dst(result.today)
        if self.model.prices != today:
            self.model.prices = today if today else []
            ret = True
        if result.tomorrow_valid:
            self.model.tomorrow_valid = True
            tomorrow = await self.model.fix_dst(result.tomorrow)
            if self.model.prices_tomorrow != tomorrow:
                self.model.prices_tomorrow = tomorrow if tomorrow else []
                ret = True
        else:
            self.model.tomorrow_valid = False
            if self.model.prices_tomorrow:
                self.model.prices_tomorrow = []
                ret = True
        await self.async_update_average([3, 7, 30])
        self.model.currency = result.currency
        self.model.use_cent = result.price_in_cent
        self.state = result.state
        await self.async_update_average_day(result.average)
        await self.async_update_average_month()
        await self.async_update_dynamic_max_price()
        return ret

    #not for peaqnext
    async def async_update_dynamic_max_price(self):
        if len(self.model.average_data) > 3:
            _dynamic_max_price = await self._dynamic_top_price.async_get_max(
                list(self.model.average_data.values())
            )
            if self.model.dynamic_top_price != _dynamic_max_price[0]:
                self.model.dynamic_top_price_type = _dynamic_max_price[1].value
                self.model.dynamic_top_price = _dynamic_max_price[0]
                await self.observer.async_broadcast(
                    ObserverTypes.DynamicMaxPriceChanged, _dynamic_max_price[0]
                )

    async def async_update_average_month(self) -> None:
        _new = self._get_average(datetime.now().day)
        if (
            len(self.model.average_data) >= int(datetime.now().day)
            and self.model.average_month != _new
        ):
            self.model.average_month = _new
            if self.model.average_month is not None:
                _LOGGER.debug(f"broadcasting average month: {_new}")
                await self.observer.async_broadcast(
                    ObserverTypes.MonthlyAveragePriceChanged, _new
                )

    async def async_update_average(self, length: list[int]) -> None:
        averages_dict = {
            3: "average_three_days",
            7: "average_weekly",
            30: "average_30",
        }
        for l in length:
            _new = self._get_average(l)
            if len(self.model.average_data) >= l and getattr(self.model, averages_dict[l]) != _new:
                setattr(self.model, averages_dict[l], _new)
                _LOGGER.debug(f"average {str(l)} updated to {_new}")
        await self.async_update_adjusted_average()

    async def async_update_adjusted_average(self) -> None:
        adj_avg: float|None = None
        if len(self.model.average_data) >= 7:
            adj_avg = max(self.model.average_weekly, self.model.average_three_days)
        elif len(self.model.average_data) >= 3:
            adj_avg = self.model.average_three_days
        if self.model.adjusted_average != adj_avg and adj_avg is not None:
            self.model.adjusted_average = adj_avg
            await self.observer.async_broadcast(
                ObserverTypes.AdjustedAveragePriceChanged, adj_avg
            )

    async def async_update_average_day(self, average) -> None:
        if average != self.model.daily_average:
            self.model.daily_average = average
            await self.async_add_average_data(average)
            await self.observer.async_broadcast(
                ObserverTypes.DailyAveragePriceChanged, average
            )

    async def async_import_average_data(self, incoming: list|dict):
        if len(incoming):
            self.model.create_date_dict(incoming)
        await self.async_cap_average_data_length()
        await self.async_update_spotprice()

    async def async_add_average_data(self, new_val):
        if isinstance(new_val, float):
            rounded = round(new_val, 3)
            if datetime.now().date not in self.model.average_data.keys():
                self.model.average_data[date.today()] = rounded
            await self.async_cap_average_data_length()

    async def async_cap_average_data_length(self):
        while len(self.model.average_data) > AVERAGE_MAX_LEN:
            min_key = min(self.model.average_data.keys())
            del self.model.average_data[min_key]

    def _get_average(self, days: int) -> float:
        try:
            if len(self.model.average_data) > days:
                avg_values = list(self.model.average_data.values())
                ret = avg_values[-days:]
            elif len(self.model.average_data) == 0:
                return 0
            else:
                ret = list(self.model.average_data.values())
            return round(mean(ret), 2)
        except Exception as e:
            _LOGGER.debug(
                f"Could not calculate average. indata: {list(self.model.average_data.values())}, error: {e}"
            )
            return 0







