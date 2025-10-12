"""Tests for SpotPriceFactory GE-Spot integration."""
import sys
from unittest.mock import Mock, MagicMock
import pytest

# Mock homeassistant before importing our modules
sys.modules['homeassistant'] = MagicMock()
sys.modules['homeassistant.helpers'] = MagicMock()
sys.modules['homeassistant.helpers.template'] = MagicMock()

from peaqevcore.common.spotprice.spotprice_factory import SpotPriceFactory
from peaqevcore.common.spotprice.models.spotprice_type import SpotPriceType
from peaqevcore.common.spotprice.gespot import GESpotUpdater
from peaqevcore.common.models.peaq_system import PeaqSystem


class TestSpotPriceFactoryGESpot:
    """Test SpotPriceFactory with GE-Spot."""
    
    def test_sources_includes_gespot(self):
        """Test that factory sources includes GESpot."""
        assert SpotPriceType.GESpot in SpotPriceFactory.sources
        assert SpotPriceFactory.sources[SpotPriceType.GESpot] == GESpotUpdater
    
    def test_gespot_enum_value(self):
        """Test that GESpot enum has correct value."""
        assert SpotPriceType.GESpot.value == "ge_spot"
    
    def test_all_price_types_have_updaters(self):
        """Test that all spot price types have corresponding updaters."""
        # Verify factory has entries for all non-Auto types
        expected_types = [
            SpotPriceType.NordPool,
            SpotPriceType.EnergidataService,
            SpotPriceType.GESpot
        ]
        
        for price_type in expected_types:
            assert price_type in SpotPriceFactory.sources
            assert SpotPriceFactory.sources[price_type] is not None
