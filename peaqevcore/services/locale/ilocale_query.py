from datetime import datetime
from abc import abstractmethod
from .querytypes.queryservice import QueryService
from ...models.locale.peaks_model import PeaksModel
from ...models.locale.sumcounter import SumCounter
from ...models.locale.price.locale_price import LocalePrice

class ILocaleQuery:

    @property
    @abstractmethod
    def dt(self) -> datetime:
        pass


    @abstractmethod
    def set_mock_dt(self, val: datetime | None):
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @property
    @abstractmethod
    def peaks(self) -> PeaksModel:
        pass

    @property
    @abstractmethod
    def sum_counter(self) -> SumCounter:
        pass

    @property
    @abstractmethod
    def charged_peak(self) -> float:
        pass

    @property
    @abstractmethod
    def observed_peak(self) -> float:
        pass

    @property
    @abstractmethod
    def price(self) -> LocalePrice:
        pass
    
    @price.setter
    @abstractmethod
    def price(self, value: LocalePrice):
        pass

    @abstractmethod
    def _sanitize_values(self):
        pass

    @abstractmethod
    async def async_reset(self) -> None:
        pass

    @abstractmethod
    async def async_set_query_service(self, service: QueryService) -> None:
        pass

    @abstractmethod
    async def async_try_update(self, new_val, timestamp: datetime | None = None):
        pass

    @abstractmethod
    async def async_set_update_for_groupby(self, new_val, dt):
        pass

    @abstractmethod
    async def async_update_peaks(self):
        pass

    @abstractmethod
    async def async_reset_values(self, new_val, dt=datetime.now()):
        pass

    @abstractmethod
    async def async_sanitize_values(self):
        pass

    @abstractmethod
    def get_currently_obeserved_peak(self, timestamp: datetime = datetime.now()) -> float:
        pass