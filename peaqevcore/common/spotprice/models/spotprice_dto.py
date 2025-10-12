import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from statistics import mean, stdev
from datetime import date, datetime
from typing import Callable

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
        self.affected_date = self._set_affected_date(self.affected_date, ret)

    @abstractmethod
    def _set_price_in_cent(self, ret) -> bool:
        pass

    @abstractmethod
    def _set_average(self, ret) -> float:
        pass

    @abstractmethod
    def _set_affected_date(self, affected_date, ret) -> date:
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

    def _set_affected_date(self, affected_date, ret) -> date:
        return datetime.now().date()


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

    def _set_affected_date(self, affected_date: date, ret) -> date:
        try:
            rawdata = ret.attributes.get("raw_today", [])
            if not len (rawdata):
                _LOGGER.warning("No rawdata found for today")
                return affected_date
            new_date = rawdata[0]['start'].date()
            if rawdata and affected_date is None or affected_date != new_date:
                _LOGGER.debug(f"successfully setting {new_date} as spotprice affected date")
                return new_date
            else:
                _LOGGER.warning(
                    f"Unable to produce affected date for today. the data I got to play with was: {new_date}")
                return affected_date
        except Exception as e:
            _LOGGER.exception("Unable to parse date from raw_today data. Settings today's date as the valid one.", e)
            return datetime.now().date()


class GESpotDTO(ISpotPriceDTO):
    """Data Transfer Object for GE-Spot integration.
    
    GE-Spot provides electricity prices with 15-minute intervals (96 per day).
    This DTO aggregates the data to hourly intervals for compatibility.
    """
    
    def _set_price_in_cent(self, ret) -> bool:
        """Detect if prices are in cents based on magnitude."""
        # GE-Spot doesn't explicitly mark cent vs currency unit
        # Heuristic: if average price > 50, likely in cents (öre/cents)
        try:
            avg_val = ret.attributes.get("average", 0)
            if avg_val and float(avg_val) > 50:
                return True
            return False
        except Exception:
            return False

    def _set_average(self, ret) -> float:
        """Get average price from GE-Spot attributes or calculate from today's prices."""
        try:
            # Try to get average from attributes
            avg_attr = ret.attributes.get("average")
            if avg_attr is not None:
                return round(float(avg_attr), 2)
            
            # Fallback: calculate from today's prices if available
            if self.today and len(self.today) > 0:
                return round(mean(self.today), 2)
            
            return 0
        except Exception as e:
            _LOGGER.exception(
                f"Could not parse average price from GE-Spot. Error: {e}"
            )
            return 0

    def _set_affected_date(self, affected_date: date, ret) -> date:
        """Determine the date for which the prices are valid."""
        try:
            # Try to get date from interval_prices keys if available
            interval_prices = ret.attributes.get("interval_prices", {})
            if interval_prices:
                # Get first timestamp and extract date
                first_time = next(iter(interval_prices.keys()), None)
                if first_time:
                    # Parse time and get today's date
                    return datetime.now().date()
            
            # Fallback to current date
            return datetime.now().date()
        except Exception as e:
            _LOGGER.warning(f"Unable to parse affected date for GE-Spot: {e}")
            return datetime.now().date()
    
    async def set_model(self, ret):
        """Override to handle GE-Spot specific data parsing.
        
        GE-Spot has 96 intervals per day (15-minute intervals).
        We aggregate to hourly for compatibility.
        """
        try:
            # Get today's prices (96 intervals)
            raw_today = ret.attributes.get("today", [])
            
            # Convert to hourly by taking average of 4 intervals
            self.today = self._aggregate_to_hourly(raw_today)
            
        except Exception as e:
            _LOGGER.exception(
                f"Could not parse today's prices from GE-Spot. Error: {e}"
            )
            self.today = []
        
        # Process tomorrow's prices
        self.tomorrow_valid = bool(ret.attributes.get("tomorrow_valid", False))
        _tomorrow = ret.attributes.get("tomorrow", [])
        
        if _tomorrow is not None and len(_tomorrow) > 0:
            self.tomorrow = self._aggregate_to_hourly(_tomorrow)
        else:
            self.tomorrow = []
        
        # Other attributes
        self.currency = str(ret.attributes.get("currency", ""))
        self.state = ret.state
        self.average = self._set_average(ret)
        self.stdev = stdev(self.today) if len(self.today) > 1 else 0
        self.price_in_cent = self._set_price_in_cent(ret)
        self.affected_date = self._set_affected_date(self.affected_date, ret)
    
    def _aggregate_to_hourly(self, interval_data: list) -> list:
        """Aggregate 15-minute intervals to hourly data.
        
        GE-Spot provides 96 intervals (15-min), we need 24 hours.
        Take average of every 4 intervals to create hourly data.
        
        Args:
            interval_data: List of 96 price values (15-min intervals)
            
        Returns:
            List of 24 price values (hourly averages)
        """
        if not interval_data:
            return []
        
        try:
            # If already 24 values, return as-is (already hourly)
            if len(interval_data) == 24:
                return list(interval_data)
            
            # If 96 values (15-min intervals), aggregate to hourly
            if len(interval_data) == 96:
                hourly_prices = []
                for hour in range(24):
                    # Get 4 intervals for this hour (15-min * 4 = 60 min)
                    start_idx = hour * 4
                    end_idx = start_idx + 4
                    hour_intervals = interval_data[start_idx:end_idx]
                    
                    # Calculate average, filtering None values
                    valid_prices = [p for p in hour_intervals if p is not None]
                    if valid_prices:
                        hourly_prices.append(round(mean(valid_prices), 3))
                    else:
                        hourly_prices.append(None)
                
                return hourly_prices
            
            # For other lengths, log warning and return as-is
            _LOGGER.warning(
                f"Unexpected interval count from GE-Spot: {len(interval_data)}. "
                f"Expected 24 (hourly) or 96 (15-min). Returning as-is."
            )
            return list(interval_data)
            
        except Exception as e:
            _LOGGER.error(f"Error aggregating GE-Spot intervals to hourly: {e}")
            return list(interval_data)
