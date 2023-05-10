from .savings_model import SavingsModel
from .savings_status import SavingsStatus
from typing import Tuple
from datetime import date, datetime, timedelta
import logging

_LOGGER = logging.getLogger(__name__)


class SavingsService:
    def __init__(self, peak_price: float) -> None:
        self.model = SavingsModel(peak_price_per_kwh=peak_price)
        self._savings_peak = 0
        self._savings_trade = 0

    @property
    def status(self) -> SavingsStatus:
        return self.model.status

    @property
    def savings_peak(self) -> float:
        return self._savings_peak

    @savings_peak.setter
    def savings_peak(self, value: float) -> None:
        self._savings_peak = round(value, 2)

    @property
    def savings_trade(self) -> float:
        return self._savings_trade

    @savings_trade.setter
    def savings_trade(self, value: float) -> None:
        self._savings_trade = round(value, 2)

    @property
    def savings_total(self) -> float:
        return sum([self.savings_peak, self.savings_trade])

    async def async_export_data(self) -> dict:
        return {
            "car_connected_at": self.model.car_connected_at,
            "prices": self.model.prices,
            "consumption": self.model.consumption,
            # "peaks": self.model.peaks,
        }

    async def async_import_data(self, data: dict) -> None:
        try:
            self.model.car_connected_at = data["car_connected_at"]
            self.model.prices = data["prices"]
            self.model.consumption = data["consumption"]
        except Exception as e:
            _LOGGER.error(f"Could not import data: {e}")

    async def async_start_listen(self, connected_at: datetime | None = None) -> None:
        self.model.car_connected_at = connected_at or datetime.now()
        self.model.status = SavingsStatus.Collecting

    async def async_stop_listen(self) -> None:
        await self.model.async_reset()

    async def async_add_prices(
        self, prices: list[float], _date: date | None = None
    ) -> None:
        await self.model.async_add_prices(prices, _date)

    async def async_add_to_consumption(
        self,
        consumption: float,
        _date: date | None = None,
        _hour: int | None = None,
    ) -> None:
        await self.model.async_add_to_consumption(consumption, _date, _hour)

    async def async_register_charge_session(
        self, charge_session: dict, original_peak: float | None = None
    ) -> None:
        estimated_power, total_energy = await self.async_calculate_estimated_power(
            charge_session
        )
        simulated_cost = await self.async_direct_charge_cost(
            estimated_power, total_energy
        )
        charge_cost = await self.async_calculate_charge_cost(charge_session)
        peaks_increase = await self.async_direct_peak_cost(
            charge_session, original_peak
        )
        self.savings_peak = peaks_increase
        self.savings_trade = max(simulated_cost - charge_cost, 0)

    async def async_direct_peak_cost(
        self, charge_session: dict, original_peak: float | None
    ) -> float:
        ret = 0
        if original_peak is None:
            return ret
        observed_peak = original_peak
        for key, value in charge_session.items():
            peaks = self.model.consumption.get(key, None)
            if peaks is None:
                _LOGGER.error(f"Could not find peaks for date {key}.")
                return 0
                # raise Exception
            for hour, energy in value.items():
                if energy + self.model.consumption[key][hour] > observed_peak:
                    ret = energy + self.model.consumption[key][hour]
                    observed_peak = energy + self.model.consumption[key][hour]
        diff = ret - original_peak
        if diff < 0:
            return 0
        return diff * self.model.peak_price_per_kwh

    async def async_direct_charge_cost(
        self, estimated_power: int, total_energy: float
    ) -> float:
        ret = 0
        dt = self.model.car_connected_at
        if dt is None:
            dt = datetime.now()
        while total_energy > 0:
            power_key = estimated_power / 1000
            ret += min(total_energy, power_key) * self.model.prices[dt.date()][dt.hour]
            total_energy -= min(total_energy, power_key)
            dt += timedelta(hours=1)
        return ret

    async def async_calculate_charge_cost(self, charge_session: dict) -> float:
        ret = 0
        for key, value in charge_session.items():
            prices = self.model.prices.get(key, None)
            if prices is None:
                raise Exception
            for hour, power in value.items():
                ret += power * prices[hour]
        return ret

    async def async_calculate_estimated_power(
        self, charge_session: dict
    ) -> Tuple[int, float]:
        ret = {}
        ret_idx = 0
        for key, value in charge_session.items():
            for hour, power in value.items():
                ret[ret_idx] = power * 1000
                ret_idx += 1
        try:
            return int(sum(ret.values()) / len(ret)), sum(ret.values()) / 1000
        except ZeroDivisionError:
            """there has been no charging. return 0. Should this be decided before this function?"""
            # _LOGGER.error("Could not calculate estimated power for savings.")
            return 0, 0
