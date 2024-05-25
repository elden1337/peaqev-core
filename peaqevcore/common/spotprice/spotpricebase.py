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


class SpotPriceBase:
    def __init__(
            self,
            hub,
            source: str,
            system: PeaqSystem,
            observer = MockObserver(),
            test:bool = False,
            is_active: bool = True,
            custom_sensor: str = None
    ):
        _LOGGER.debug(f"Initializing Spotprice for {source} from system {system.value}.")
        self.hub = hub
        self.observer = observer #not used?
        self.model = SpotPriceModel(source=source)
        self._dynamic_top_price = DynamicTopPrice()
        self._is_initialized: bool = False
        self._custom_sensor: str = custom_sensor
        if not test:
            self.state_machine = hub.state_machine
            if is_active:
                self.setup()

    @property
    def custom_sensor(self) -> str|None:
        return self._custom_sensor

    @property
    def tomorrow_valid(self) -> bool:
        return self.model.tomorrow_valid

    @property
    def entity(self) -> str:
        return self.model.entity

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
    
    @property
    def average_stdev_data(self) -> dict[date, float]:
        return self.model.average_stdev_data


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
        else:
            _LOGGER.warning("No entity set for Spotprice. Unable to calculate price-data")

    def callback_export_prices(self):
        return [self.model.prices, self.model.prices_tomorrow]

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
        
        self.model.currency = result.currency
        self.model.use_cent = result.price_in_cent
        self.state = result.state
        if result.affected_date == datetime.now().date():
            await self.async_update_average([3, 7, 30])
            await self.async_update_average_day(result.average, result.affected_date)
            await self.async_add_average_stdev_data(result.stdev, result.affected_date)
            await self.async_update_average_month()
            await self.async_update_dynamic_max_price()
        else:
            _LOGGER.warning(f"Possible issue detected with {result.affected_date} in {self.source} dates.")
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
                await self.hub.observer.async_broadcast(
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
                await self.hub.observer.async_broadcast(
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
            await self.hub.observer.async_broadcast(
                ObserverTypes.AdjustedAveragePriceChanged, adj_avg
            )

    async def async_update_average_day(self, average, checkdate) -> None:
        await self.async_add_average_data(average, checkdate)
        if average != self.model.daily_average or self.model.daily_average_date != checkdate:
            if average != self.model.daily_average and self.model.daily_average_date == checkdate:
                self.model.patch_average_data()
            self.model.daily_average = average
            self.model.daily_average_date = checkdate
            await self.hub.observer.async_broadcast(
                ObserverTypes.DailyAveragePriceChanged, average
            )

    async def async_import_average_data(self, incoming_prices: list|dict, incoming_stdev: list|dict|None = None):
        if len(incoming_prices):
            self.model.average_data = incoming_prices
        await self.async_cap_average_data_length(self.model.average_data)

        if incoming_stdev is not None and len(incoming_stdev):
            self.model.average_stdev_data = incoming_stdev
        await self.async_cap_average_data_length(self.model.average_stdev_data)
        await self.async_update_spotprice()

    async def async_add_average_data(self, new_val, checkdate: date):
        if isinstance(new_val, float):
            rounded = round(new_val, 3)
            if not checkdate in [d for d in self.model.average_data.keys()]:
                _LOGGER.debug(f"Attempting add average spotprice data: {rounded}, keys: {self.model.average_data.keys()}")
            elif self.model.average_data[checkdate] != rounded:
                _LOGGER.debug(f"Average spotprice data already exists for {checkdate} as {self.model.average_data[checkdate]}. Updating to {rounded}")
            self.model.update_average_data(checkdate, rounded)

            await self.async_cap_average_data_length(self.model.average_data)

    async def async_add_average_stdev_data(self, new_val, checkdate):
        if isinstance(new_val, float):
            rounded = round(new_val, 3)
            if checkdate not in self.model.average_stdev_data.keys():
                _LOGGER.debug(
                    f"Attempting add average stdev data: {rounded}, keys: {self.model.average_data.keys()}")
            elif self.model.average_stdev_data[checkdate] != rounded:
                _LOGGER.debug(
                    f"Average stdev data already exists for {checkdate} as {self.model.average_stdev_data[checkdate]}. Updating to {rounded}")
            self.model.update_average_stdev_data(date.today(), rounded)
            await self.async_cap_average_data_length(self.model.average_stdev_data)

    async def async_cap_average_data_length(self, data: dict):
        while len(data) > AVERAGE_MAX_LEN:
            min_key = min(data.keys())
            del data[min_key]

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







