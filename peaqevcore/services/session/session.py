from .session_service import SessionService
import logging

_LOGGER = logging.getLogger(__name__)


class Session:
    def __init__(self, charger):
        self._charger = charger
        self.service: SessionService = SessionService()

    async def async_setup(self):
        await self.service.async_setup()

    @property
    def session_energy(self):
        return self.service.total_energy

    @property
    def session_data(self) -> dict:
        return self.service.session_data

    @property
    def original_peak(self) -> float:
        return self.service.original_peak

    async def async_set_session_energy(self, val):
        await self.service.async_update_power_reading(val)
        await self.async_update_session_pricing()

    @property
    def session_price(self):
        return self.service.total_price

    async def async_set_session_price(self, val) -> None:
        await self.service.async_update_price(val)
        await self.async_update_session_pricing()

    @property
    def energy_average(self) -> float:
        return self.service.energy_average

    @property
    def energy_weekly_dict(self) -> dict:
        return self.service.energy_weekly_dict

    async def async_update_session_pricing(self):
        if self._charger.model.session_active is False:
            await self.async_terminate()

    async def async_terminate(self):
        await self.service.async_terminate()

    async def async_reset(self, original_peak=0):
        await self.service.async_reset(original_peak)

    async def async_unpack(self, data):
        await self.service.average_data.async_unpack(data)

    async def async_setup_fresh(self):
        await self.service.average_data.async_set_init_model()
