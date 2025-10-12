"""Tests for GE-Spot integration."""
import sys
from unittest.mock import Mock, AsyncMock, MagicMock

# Mock homeassistant before importing our modules
sys.modules['homeassistant'] = MagicMock()
sys.modules['homeassistant.helpers'] = MagicMock()
sys.modules['homeassistant.helpers.template'] = MagicMock()

# flake8: noqa: E402
import pytest
from datetime import datetime

from peaqevcore.common.spotprice.models.spotprice_dto import GESpotDTO
from peaqevcore.common.spotprice.gespot import GESpotUpdater
from peaqevcore.common.spotprice.const import GESPOT
from peaqevcore.common.models.peaq_system import PeaqSystem


class TestGESpotDTO:
    """Test GESpotDTO data transformation."""

    def test_aggregate_to_hourly_96_intervals(self):
        """Test aggregation of 96 intervals to 24 hours."""
        dto = GESpotDTO()

        # Create 96 test values (4 per hour)
        test_data = [float(i) for i in range(96)]

        result = dto._aggregate_to_hourly(test_data)

        assert len(result) == 24
        # First hour: average of [0,1,2,3] = 1.5
        assert result[0] == 1.5
        # Second hour: average of [4,5,6,7] = 5.5
        assert result[1] == 5.5

    def test_aggregate_to_hourly_24_intervals(self):
        """Test that 24 intervals are returned as-is."""
        dto = GESpotDTO()

        test_data = [float(i) for i in range(24)]

        result = dto._aggregate_to_hourly(test_data)

        assert len(result) == 24
        assert result == test_data

    def test_aggregate_to_hourly_empty(self):
        """Test handling of empty data."""
        dto = GESpotDTO()

        result = dto._aggregate_to_hourly([])

        assert result == []

    def test_aggregate_to_hourly_with_none_values(self):
        """Test aggregation with None values."""
        dto = GESpotDTO()

        # Create test data with some None values
        test_data = [1.0, 2.0, None, 3.0] * 24  # 96 values

        result = dto._aggregate_to_hourly(test_data)

        assert len(result) == 24
        # First hour: average of [1.0, 2.0, 3.0] = 2.0 (None filtered out)
        assert result[0] == 2.0

    def test_set_price_in_cent_high_value(self):
        """Test cent detection with high values."""
        dto = GESpotDTO()

        mock_ret = Mock()
        mock_ret.attributes = {"average": 75.5}

        result = dto._set_price_in_cent(mock_ret)

        assert result is True

    def test_set_price_in_cent_low_value(self):
        """Test cent detection with low values."""
        dto = GESpotDTO()

        mock_ret = Mock()
        mock_ret.attributes = {"average": 1.23}

        result = dto._set_price_in_cent(mock_ret)

        assert result is False

    def test_set_average_from_attribute(self):
        """Test getting average from attributes."""
        dto = GESpotDTO()

        mock_ret = Mock()
        mock_ret.attributes = {"average": 45.67}

        result = dto._set_average(mock_ret)

        assert result == 45.67

    def test_set_average_calculated(self):
        """Test calculating average from today's prices."""
        dto = GESpotDTO()
        dto.today = [1.0, 2.0, 3.0, 4.0]

        mock_ret = Mock()
        mock_ret.attributes = {}

        result = dto._set_average(mock_ret)

        assert result == 2.5  # mean of [1,2,3,4]

    def test_set_affected_date(self):
        """Test setting affected date."""
        dto = GESpotDTO()

        mock_ret = Mock()
        mock_ret.attributes = {"interval_prices": {"00:00": 1.0}}

        result = dto._set_affected_date(None, mock_ret)

        assert result == datetime.now().date()

    @pytest.mark.asyncio
    async def test_set_model_full(self):
        """Test full model setup with 96 intervals."""
        dto = GESpotDTO()

        # Mock sensor state
        mock_ret = Mock()
        mock_ret.state = 1.23
        mock_ret.attributes = {
            "today": [float(i) for i in range(96)],
            "tomorrow": [float(i + 100) for i in range(96)],
            "tomorrow_valid": True,
            "currency": "SEK",
            "average": 47.5
        }

        await dto.set_model(mock_ret)

        assert len(dto.today) == 24
        assert len(dto.tomorrow) == 24
        assert dto.tomorrow_valid is True
        assert dto.currency == "SEK"
        assert dto.state == 1.23
        assert dto.average == 47.5
        assert dto.price_in_cent is False  # 47.5 is < 50


class TestGESpotUpdater:
    """Test GESpotUpdater class."""

    def test_init(self):
        """Test initialization."""
        mock_hub = Mock()
        mock_observer = Mock()

        updater = GESpotUpdater(
            hub=mock_hub,
            observer=mock_observer,
            system=PeaqSystem.PeaqHvac,
            test=True
        )

        assert updater.source == GESPOT

    @pytest.mark.asyncio
    async def test_async_set_dto_initial(self):
        """Test DTO setup on initial load."""
        mock_hub = Mock()
        mock_hub.async_update_prices = AsyncMock()
        mock_hub.observer = Mock()
        mock_hub.observer.async_broadcast = AsyncMock()

        mock_observer = Mock()
        mock_observer.async_broadcast = AsyncMock()

        updater = GESpotUpdater(
            hub=mock_hub,
            observer=mock_observer,
            system=PeaqSystem.PeaqHvac,
            test=True
        )

        # Mock the async_update_set_prices to return True
        updater.async_update_set_prices = AsyncMock(return_value=True)
        updater.model = Mock()
        updater.model.prices = [1.0] * 24
        updater.model.prices_tomorrow = [2.0] * 24

        # Mock sensor state
        mock_ret = Mock()
        mock_ret.state = 1.23
        mock_ret.attributes = {
            "today": [float(i) for i in range(96)],
            "tomorrow": [float(i) for i in range(96)],
            "tomorrow_valid": True,
            "currency": "SEK",
            "average": 47.5
        }

        await updater.async_set_dto(mock_ret, initial=True)

        assert updater._is_initialized is True
        mock_hub.async_update_prices.assert_called_once()
        mock_hub.observer.async_broadcast.assert_called()
