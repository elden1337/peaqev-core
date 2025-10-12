"""GE-Spot price integration for peaqevcore."""
import asyncio
import logging

import homeassistant.helpers.template as template

from peaqevcore.common.models.observer_types import ObserverTypes
from peaqevcore.common.spotprice.const import GESPOT
from peaqevcore.common.spotprice.models.spotprice_dto import GESpotDTO
from peaqevcore.common.spotprice.spotpricebase import SpotPriceBase
from peaqevcore.common.models.peaq_system import PeaqSystem

_LOGGER = logging.getLogger(__name__)


class GESpotUpdater(SpotPriceBase):
    """GE-Spot price updater.

    Handles electricity spot price data from the GE-Spot integration,
    which provides global electricity spot prices with 15-minute intervals.
    """

    def __init__(
        self,
        hub,
        observer,
        system: PeaqSystem,
        test: bool = False,
        is_active: bool = True,
        custom_sensor: str = None
    ):
        """Initialize GE-Spot updater."""
        super().__init__(
            hub=hub,
            source=GESPOT,
            system=system,
            test=test,
            is_active=is_active,
            observer=observer,
            custom_sensor=custom_sensor
        )

    async def async_set_dto(self, ret, initial: bool = False) -> None:
        """Set data transfer object from sensor state.

        Args:
            ret: Sensor state object from Home Assistant
            initial: Whether this is the initial setup
        """
        _result = GESpotDTO()
        await _result.set_model(ret)

        if await self.async_update_set_prices(_result):
            if initial:
                await self.hub.async_update_prices(
                    [self.model.prices, self.model.prices_tomorrow]
                )
                _LOGGER.info("GE-Spot service has been successfully initialized.")
                _LOGGER.debug("GE-Spot service initialized. Broadcasting...")
                await self.hub.observer.async_broadcast(
                    ObserverTypes.SpotpriceInitialized
                )
            else:
                await self.hub.observer.async_broadcast(
                    ObserverTypes.PricesChanged,
                    [self.model.prices, self.model.prices_tomorrow]
                )
            self._is_initialized = True

    def setup(self):
        """Set up the GE-Spot integration.

        Discovers GE-Spot entities and initializes the price updater.
        Supports both automatic discovery and custom sensor specification.
        """
        try:
            # If custom sensor is specified, use it directly
            if self.custom_sensor:
                _LOGGER.info(
                    f"Using custom sensor for GE-Spot prices: {self.custom_sensor}"
                )
                self._setup_set_entity(self.custom_sensor)
                return

            # Discover GE-Spot entities
            entities = template.integration_entities(self.state_machine, GESPOT)
            entities_list = list(entities)

            _LOGGER.debug(
                f"Found {len(entities_list)} GE-Spot entities: {entities_list}"
            )

            # No entities found
            if len(entities_list) < 1:
                if hasattr(self.hub.options, "price"):
                    self.hub.options.price.price_aware = False
                _LOGGER.error(
                    "No GE-Spot entities found. Cannot continue with price-awareness."
                )
                return

            # Single entity - use it
            if len(entities_list) == 1:
                self._setup_set_entity(entities_list[0])
                return

            # Multiple entities - try to find the best one
            # GE-Spot entities typically follow pattern: sensor.gespot_current_price_<area>
            # Look for "current_price" in entity ID
            best_entity = None
            for entity in entities_list:
                if "current_price" in entity.lower():
                    best_entity = entity
                    break

            if best_entity:
                _LOGGER.info(
                    f"Multiple GE-Spot entities found, using: {best_entity}"
                )
                self._setup_set_entity(best_entity)
            else:
                # Fallback to first entity
                _LOGGER.warning(
                    f"Multiple GE-Spot entities found, using first one: {entities_list[0]}"
                )
                self._setup_set_entity(entities_list[0])

        except Exception as e:
            if hasattr(self.hub.options, "price"):
                self.hub.options.price.price_aware = False
            _LOGGER.error(
                f"Unable to set up GE-Spot integration. Error: {e}",
                exc_info=True
            )

    def _setup_set_entity(self, entity: str) -> None:
        """Configure the entity and start price updates.

        Args:
            entity: Entity ID of the GE-Spot sensor
        """
        self.model.entity = entity
        _LOGGER.debug(
            f"GE-Spot has been set up and is ready to use with {self.model.entity}"
        )
        asyncio.run_coroutine_threadsafe(
            self.async_update_spotprice(initial=True),
            self.state_machine.loop,
        )
