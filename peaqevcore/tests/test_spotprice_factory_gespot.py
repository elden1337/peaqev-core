"""Tests for SpotPriceFactory GE-Spot integration."""
import pytest
from unittest.mock import Mock, MagicMock

from peaqevcore.common.spotprice.spotprice_factory import SpotPriceFactory
from peaqevcore.common.spotprice.models.spotprice_type import SpotPriceType
from peaqevcore.common.spotprice.gespot import GESpotUpdater
from peaqevcore.common.spotprice.nordpool import NordPoolUpdater
from peaqevcore.common.spotprice.energidataservice import EnergiDataServiceUpdater
from peaqevcore.common.models.peaq_system import PeaqSystem
from peaqevcore.common.spotprice.const import GESPOT, ENERGIDATASERVICE_SENSOR


class TestSpotPriceFactoryGESpot:
    """Test SpotPriceFactory with GE-Spot."""
    
    def test_sources_includes_gespot(self):
        """Test that factory sources includes GESpot."""
        assert SpotPriceType.GESpot in SpotPriceFactory.sources
        assert SpotPriceFactory.sources[SpotPriceType.GESpot] == GESpotUpdater
    
    def test_test_connections_detects_gespot(self):
        """Test that GE-Spot is detected when entities exist."""
        mock_hass = Mock()
        mock_hass.states.get.return_value = None
        
        # Mock template.integration_entities to return GE-Spot entities
        with pytest.mock.patch('homeassistant.helpers.template.integration_entities') as mock_integration:
            mock_integration.return_value = ['sensor.gespot_current_price_se4']
            
            result = SpotPriceFactory.test_connections(
                mock_hass,
                SpotPriceType.NordPool,
                PeaqSystem.Peaq
            )
            
            assert result == SpotPriceType.GESpot
    
    def test_test_connections_gespot_priority_over_eds(self):
        """Test that GE-Spot has priority over EnergiDataService."""
        mock_hass = Mock()
        # EDS sensor exists
        mock_hass.states.get.return_value = Mock()
        
        # GE-Spot also exists
        with pytest.mock.patch('homeassistant.helpers.template.integration_entities') as mock_integration:
            mock_integration.return_value = ['sensor.gespot_current_price_se4']
            
            result = SpotPriceFactory.test_connections(
                mock_hass,
                SpotPriceType.NordPool,
                PeaqSystem.Peaq
            )
            
            # Should return GESpot, not EnergiDataService
            assert result == SpotPriceType.GESpot
    
    def test_test_connections_fallback_without_gespot(self):
        """Test fallback when GE-Spot is not available."""
        mock_hass = Mock()
        mock_hass.states.get.return_value = None
        
        # No GE-Spot entities
        with pytest.mock.patch('homeassistant.helpers.template.integration_entities') as mock_integration:
            mock_integration.return_value = []
            
            result = SpotPriceFactory.test_connections(
                mock_hass,
                SpotPriceType.NordPool,
                PeaqSystem.Peaq
            )
            
            # Should fallback to Nordpool
            assert result == SpotPriceType.NordPool
    
    def test_test_connections_respects_peaqev_nordpool(self):
        """Test that PeaqEv + Nordpool combo is respected."""
        mock_hass = Mock()
        
        # Even with GE-Spot available
        with pytest.mock.patch('homeassistant.helpers.template.integration_entities') as mock_integration:
            mock_integration.return_value = ['sensor.gespot_current_price_se4']
            
            result = SpotPriceFactory.test_connections(
                mock_hass,
                SpotPriceType.NordPool,
                PeaqSystem.PeaqEv  # PeaqEv system
            )
            
            # Should still return Nordpool due to PeaqEv legacy
            assert result == SpotPriceType.NordPool
    
    def test_create_returns_gespot_updater(self):
        """Test that create() returns GESpotUpdater when appropriate."""
        mock_hub = Mock()
        mock_hub.state_machine = Mock()
        mock_hub.state_machine.states.get.return_value = None
        
        mock_observer = Mock()
        
        with pytest.mock.patch('homeassistant.helpers.template.integration_entities') as mock_integration:
            mock_integration.return_value = ['sensor.gespot_current_price_se4']
            
            with pytest.mock.patch.object(GESpotUpdater, '__init__', return_value=None) as mock_init:
                result = SpotPriceFactory.create(
                    hub=mock_hub,
                    observer=mock_observer,
                    system=PeaqSystem.Peaq,
                    spotprice_type=SpotPriceType.NordPool
                )
                
                # Should have tried to create GESpotUpdater
                assert isinstance(result, GESpotUpdater)
    
    def test_create_with_custom_sensor(self):
        """Test create() with custom GE-Spot sensor."""
        mock_hub = Mock()
        mock_hub.state_machine = Mock()
        mock_hub.state_machine.states.get.return_value = None
        
        mock_observer = Mock()
        custom_sensor = "sensor.my_custom_gespot"
        
        with pytest.mock.patch('homeassistant.helpers.template.integration_entities') as mock_integration:
            # Return empty list, but custom sensor should still work
            mock_integration.return_value = []
            
            with pytest.mock.patch.object(GESpotUpdater, '__init__', return_value=None):
                with pytest.mock.patch.object(GESpotUpdater, 'setup') as mock_setup:
                    result = SpotPriceFactory.create(
                        hub=mock_hub,
                        observer=mock_observer,
                        system=PeaqSystem.Peaq,
                        spotprice_type=SpotPriceType.GESpot,
                        custom_sensor=custom_sensor
                    )
                    
                    assert isinstance(result, GESpotUpdater)
