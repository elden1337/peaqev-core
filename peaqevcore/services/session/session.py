from .session_price import SessionPrice
import logging

_LOGGER = logging.getLogger(__name__)


class Session:
    def __init__(self, charger):
        self._charger = charger
        self.core: SessionPrice = SessionPrice()

    async def async_setup(self):
        await self.core.async_setup()

    @property
    def session_energy(self):
        return self.core.total_energy

    async def async_update_session_energy(self, val):
        await self.core.async_update_power_reading(val)
        await self.async_update_session_pricing()

    @property
    def session_price(self):
        return self.core.total_price

    async def async_set_session_price(self, val) -> None:
        await self.core.async_update_price(val)
        await self.async_update_session_pricing()

    @property
    def energy_average(self) -> float:
        return self.core.energy_average

    @property
    def energy_weekly_dict(self) -> dict:
        return self.core.energy_weekly_dict

    async def async_update_session_pricing(self):
        if self._charger.model.session_active is False:
            await self.async_terminate()

    async def async_terminate(self):
        await self.core.async_terminate()

    async def async_reset(self):
        await self.core.async_reset()

    async def async_unpack(self, data):
        await self.core.average_data.async_unpack(data)

    async def async_setup_fresh(self):
        await self.core.average_data.async_set_init_model()
