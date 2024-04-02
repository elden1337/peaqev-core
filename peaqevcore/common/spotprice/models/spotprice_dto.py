import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from statistics import mean, stdev
from datetime import date, datetime

_LOGGER = logging.getLogger(__name__)


@dataclass
class ISpotPriceDTO:
    state: float = 0
    today: list = field(default_factory=lambda: [])
    tomorrow: list = field(default_factory=lambda: [])
    average: float = 0
    stdev: float = 0
    currency: str = ""
    price_in_cent: bool = False
    tomorrow_valid: bool = False
    affected_date: date = None

    async def set_model(self, ret):
        try:
            self.today = list(ret.attributes.get("today"))
        except Exception as e:
            _LOGGER.exception(
                f"Could not parse today's prices. Unsolveable error. {e}"
            )
            return
        self.tomorrow_valid = bool(ret.attributes.get("tomorrow_valid", False))
        _tomorrow = ret.attributes.get("tomorrow", [])
        if _tomorrow is not None:
            self.tomorrow = list(_tomorrow)
        else:
            self.tomorrow = []
        self.currency = str(ret.attributes.get("currency", ""))
        self.state = ret.state
        self.average = self._set_average(ret)
        self.stdev = stdev(self.today) if len(self.today) > 1 else 0
        self.price_in_cent = self._set_price_in_cent(ret)
        self.affected_date = self._set_affected_date(ret)

    @abstractmethod
    def _set_price_in_cent(self, ret) -> bool:
        pass

    @abstractmethod
    def _set_average(self, ret) -> float:
        pass

    @abstractmethod
    def _set_affected_date(self, ret) -> date:
        pass


@dataclass
class EnergiDataServiceDTO(ISpotPriceDTO):

    def _set_price_in_cent(self, ret) -> bool:
            return bool(ret.attributes.get("use_cent", False))

    def _set_average(self, ret) -> float:
        try:
            return round(mean(self.today), 2)
        except Exception as e:
            _LOGGER.exception(
                f"Could not parse today's prices from EnergiDataService. Unsolveable error. {e}"
            )
            return 0

    def _set_affected_date(self, ret) -> date:
        return datetime.now().date


@dataclass
class NordpoolDTO(ISpotPriceDTO):
    
    def _set_price_in_cent(self, ret) -> bool:
        return bool(ret.attributes.get("price_in_cent", False))

    def _set_average(self, ret) -> float:
        try:
            return float(str(ret.attributes.get("average", 0)))
        except Exception as e:
            _LOGGER.exception(
                f"Could not parse today's prices from Nordpool. Unsolveable error. {e}"
            )
            return 0

    def _set_affected_date(self, ret) -> date:
        try:
            rawdata = ret.attributes.get("raw_today", {})
            if rawdata:
                return data_dict['start'].date()
            pass
        except Exception as e:
            _LOGGER.exception("blabla")
            return datetime.now().date
