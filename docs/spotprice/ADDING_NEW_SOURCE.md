# Adding a New Price Source to peaqevcore

**Audience**: Core contributors adding support for new electricity price integrations  
**Difficulty**: Intermediate  
**Time Estimate**: 4-8 hours  
**Last Updated**: October 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Guide](#step-by-step-guide)
4. [Reference Implementation](#reference-implementation)
5. [Testing Strategy](#testing-strategy)
6. [Code Review Checklist](#code-review-checklist)
7. [Common Pitfalls](#common-pitfalls)

---

## Overview

This guide walks you through adding support for a new electricity price integration to peaqevcore, following the established architectural patterns.

### What You'll Create

1. **Constant** - Identifier for your source
2. **Enum** - Type definition
3. **DTO Class** - Data transformation logic
4. **Updater Class** - Integration with Home Assistant
5. **Factory Integration** - Auto-detection logic
6. **Tests** - Comprehensive test coverage

### Example We'll Follow

We'll use **GE-Spot** as a reference implementation. It was added in v19.12.0 and follows all best practices.

---

## Prerequisites

### Knowledge Required

- ✅ Python async/await patterns
- ✅ Home Assistant entity system
- ✅ Basic understanding of peaqevcore architecture
- ✅ Familiarity with pytest

### Tools Needed

- Python 3.12+
- peaqevcore development environment
- IDE with Python support
- Access to the target price integration

### Reading List

Before starting, review:
1. [Architecture Overview](../ARCHITECTURE.md)
2. [Spot Price System](README.md)
3. [GE-Spot Implementation](GE_SPOT.md) (reference)

---

## Step-by-Step Guide

### Step 1: Add Constant

**File**: `peaqevcore/common/spotprice/const.py`

Add a constant for your price source. Use lowercase with underscores, matching the Home Assistant integration domain.

```python
# Existing constants
NORDPOOL = "nordpool"
ENERGIDATASERVICE = "energidataservice"
GESPOT = "ge_spot"

# Add your source
YOUR_SOURCE = "your_source_name"  # Match HA integration domain
```

**✅ Validation**: 
- Name matches Home Assistant integration domain exactly
- Lowercase with underscores (not camelCase or hyphens)
- No spaces or special characters

---

### Step 2: Add Enum Type

**File**: `peaqevcore/common/spotprice/models/spotprice_type.py`

Add your source to the `SpotPriceType` enum:

```python
from peaqevcore.common.spotprice.const import (
    NORDPOOL,
    ENERGIDATASERVICE,
    GESPOT,
    YOUR_SOURCE,  # Import your constant
)

class SpotPriceType(str, Enum):
    """Enum for supported spot price types."""
    
    Nordpool = NORDPOOL
    EnergidataService = ENERGIDATASERVICE
    GESpot = GESPOT
    YourSource = YOUR_SOURCE  # Add your enum value
    Auto = 'Auto'  # Keep Auto last for backward compatibility
```

**✅ Validation**:
- Enum name is PascalCase
- Uses your constant (not hardcoded string)
- `Auto` remains last in the list

---

### Step 3: Create DTO Class

**File**: `peaqevcore/common/spotprice/models/spotprice_dto.py`

Create a class to transform your price source's data format into the standard model.

```python
class YourSourceDTO(ISpotPriceDTO):
    """Data Transfer Object for YourSource price data.
    
    YourSource provides prices in [describe format].
    This DTO transforms them to the standard 24-hourly format.
    """
    
    def set_model(self, sensor_data: dict, timezone) -> None:
        """Transform YourSource data to SpotPriceModel.
        
        Args:
            sensor_data: Raw sensor data from Home Assistant
            timezone: Timezone for date calculations
        """
        # Extract attributes from sensor
        attributes = sensor_data.get("attributes", {})
        
        # Get today's prices
        today_prices = self._get_today_prices(attributes)
        
        # Get tomorrow's prices (may be empty)
        tomorrow_prices = self._get_tomorrow_prices(attributes)
        
        # Normalize data if needed
        today_prices = self._normalize_prices(today_prices)
        tomorrow_prices = self._normalize_prices(tomorrow_prices)
        
        # Calculate average
        average = self._calculate_average(attributes, today_prices)
        
        # Set affected date
        affected_date = self._set_affected_date(timezone)
        
        # Create the model
        self.model = SpotPriceModel(
            price_aware=bool(today_prices),
            today=today_prices,
            tomorrow=tomorrow_prices,
            average=average,
            affected_date=affected_date
        )
    
    def _get_today_prices(self, attributes: dict) -> list:
        """Extract and transform today's prices."""
        # Get raw prices from attributes
        raw_prices = attributes.get("today", [])
        
        # Transform if needed (e.g., 15min → hourly, cents → currency)
        # Return list of 24 floats or empty list
        return self._transform_prices(raw_prices)
    
    def _get_tomorrow_prices(self, attributes: dict) -> list:
        """Extract and transform tomorrow's prices."""
        raw_prices = attributes.get("tomorrow", [])
        return self._transform_prices(raw_prices)
    
    def _transform_prices(self, raw_prices: list) -> list:
        """Transform raw prices to 24-hourly format.
        
        Implement your source's specific transformation logic here.
        Examples:
        - Aggregate 15-minute intervals to hourly
        - Convert cents to currency units
        - Handle missing data
        """
        # Your transformation logic here
        if not raw_prices:
            return []
        
        # Example: If already 24 hourly values
        if len(raw_prices) == 24:
            return raw_prices
        
        # Example: If 96 15-minute intervals (like GE-Spot)
        if len(raw_prices) == 96:
            return self._aggregate_to_hourly(raw_prices)
        
        return []
    
    def _aggregate_to_hourly(self, prices: list) -> list:
        """Aggregate sub-hourly data to hourly averages."""
        hourly = []
        intervals_per_hour = len(prices) // 24
        
        for hour in range(24):
            start = hour * intervals_per_hour
            end = start + intervals_per_hour
            hour_values = prices[start:end]
            
            # Filter out None values
            valid = [v for v in hour_values if v is not None]
            
            if valid:
                hourly.append(sum(valid) / len(valid))
            else:
                hourly.append(None)
        
        return hourly
    
    def _normalize_prices(self, prices: list) -> list:
        """Normalize price units (e.g., convert cents to currency)."""
        if not prices:
            return prices
        
        # Auto-detect cents (heuristic: average > 50 = cents)
        valid_prices = [p for p in prices if p is not None]
        if valid_prices:
            avg = sum(valid_prices) / len(valid_prices)
            if avg > 50:  # Likely cents
                return [p / 100 if p is not None else None for p in prices]
        
        return prices
    
    def _calculate_average(self, attributes: dict, today_prices: list) -> float:
        """Calculate or extract average price."""
        # Try to get from attributes first
        for attr_name in ["average", "average_today", "mean"]:
            if attr_name in attributes:
                avg = attributes[attr_name]
                if avg:
                    # Check if in cents
                    if avg > 50:
                        return avg / 100
                    return avg
        
        # Calculate from today's prices
        if today_prices:
            valid = [p for p in today_prices if p is not None]
            if valid:
                return sum(valid) / len(valid)
        
        return 0.0
```

**Key Points**:
- ✅ Inherit from `ISpotPriceDTO`
- ✅ Implement `set_model()` method
- ✅ Handle missing/invalid data gracefully
- ✅ Return 24 hourly prices (list of 24 floats)
- ✅ Document the source's data format in docstring

---

### Step 4: Create Updater Class

**File**: Create new file `peaqevcore/common/spotprice/yoursource.py`

```python
"""YourSource price integration for peaqevcore."""
import logging
from typing import Optional

from .const import YOUR_SOURCE
from .spotpricebase import SpotPriceBase
from .models.spotprice_dto import YourSourceDTO

_LOGGER = logging.getLogger(__name__)


class YourSourceUpdater(SpotPriceBase):
    """Updater for YourSource electricity price integration.
    
    YourSource provides [describe what the integration does].
    This updater handles entity discovery and data updates.
    """
    
    def __init__(self):
        """Initialize YourSource updater with source constant."""
        super().__init__(source=YOUR_SOURCE)
        _LOGGER.debug("Initialized YourSourceUpdater")
    
    async def async_set_dto(self, hub, sensor_data: dict) -> None:
        """Transform YourSource data using YourSourceDTO.
        
        Args:
            hub: The hub instance (for timezone, etc.)
            sensor_data: Raw sensor data from Home Assistant
        """
        _LOGGER.debug(f"Setting DTO for {self.source}")
        
        # Create DTO instance
        self.dto = YourSourceDTO(sensor_data, hub.hours.timezone)
        
        # Update the model
        await self.dto.async_update()
        self.model = self.dto.model
        
        _LOGGER.debug(
            f"DTO updated - price_aware: {self.model.price_aware}, "
            f"today prices: {len(self.model.today) if self.model.today else 0}"
        )
    
    async def setup(
        self,
        hub,
        observer,
        sensor: Optional[str] = None
    ) -> bool:
        """Discover and setup YourSource entities.
        
        Args:
            hub: The hub instance
            observer: The observer for state changes
            sensor: Optional specific sensor entity_id
            
        Returns:
            True if entity found and setup succeeded, False otherwise
        """
        from homeassistant.helpers import template
        
        _LOGGER.debug(f"Setting up {self.source} integration")
        
        # Discover all YourSource entities
        entities = template.integration_entities(
            hub.state_machine,
            YOUR_SOURCE
        )
        
        if not entities:
            _LOGGER.debug(f"No {self.source} entities found")
            return False
        
        _LOGGER.info(f"Found {len(entities)} {self.source} entities: {entities}")
        
        # Choose entity
        if sensor and sensor in entities:
            # Use specified sensor
            chosen_entity = sensor
            _LOGGER.info(f"Using specified sensor: {chosen_entity}")
        else:
            # Use first available
            chosen_entity = entities[0]
            if len(entities) > 1:
                _LOGGER.warning(
                    f"Multiple {self.source} entities found, using: {chosen_entity}"
                )
        
        # Setup the entity
        await self._setup_set_entity(hub, observer, chosen_entity)
        
        return True
```

**Key Points**:
- ✅ Inherit from `SpotPriceBase`
- ✅ Call `super().__init__(source=YOUR_SOURCE)` in constructor
- ✅ Implement `async_set_dto()` using your DTO
- ✅ Implement `setup()` for entity discovery
- ✅ Use `template.integration_entities()` to find entities
- ✅ Add logging for debugging

---

### Step 5: Update Factory

**File**: `peaqevcore/common/spotprice/spotprice_factory.py`

Add your source to the factory's detection logic.

```python
# 1. Import your updater
from .yoursource import YourSourceUpdater

# 2. Add to sources dictionary
sources = {
    SpotPriceType.Nordpool: NordpoolUpdater,
    SpotPriceType.EnergidataService: EnergiDataServiceUpdater,
    SpotPriceType.GESpot: GESpotUpdater,
    SpotPriceType.YourSource: YourSourceUpdater,  # Add here
}

# 3. Update test_connections() method
@staticmethod
def test_connections(
    hass,
    spotprice_type,
    system: PeaqSystem,
    custom_sensor=None
):
    """Detect available price source and return updater class."""
    from homeassistant.helpers import template
    
    # Check for YourSource entities
    yoursource_entities = template.integration_entities(hass, YOUR_SOURCE)
    if yoursource_entities:
        _LOGGER.debug("Found YourSource entities, using YourSourceUpdater")
        return sources[SpotPriceType.YourSource]
    
    # Check for GE-Spot entities
    gespot_entities = template.integration_entities(hass, GESPOT)
    if gespot_entities:
        _LOGGER.debug("Found GE-Spot entities, using GESpotUpdater")
        return sources[SpotPriceType.GESpot]
    
    # ... existing detection logic
    
    # Fallback to Nordpool
    _LOGGER.debug("Using Nordpool as fallback")
    return sources[SpotPriceType.Nordpool]
```

**Priority Considerations**:

Place your source in the detection order based on:
- **Specificity**: More specific sources (e.g., country-specific) lower priority than general
- **Coverage**: Wider geographic coverage = higher priority
- **Reliability**: More reliable sources = higher priority
- **Fallback Support**: Sources with fallbacks = higher priority

**Current Order**:
1. GE-Spot (multi-region, fallbacks)
2. EnergiDataService (Denmark official)
3. Nordpool (Nordic established)

---

### Step 6: Write Tests

**File**: Create new file `peaqevcore/tests/test_yoursource.py`

```python
"""Tests for YourSource integration."""
import sys
from unittest.mock import Mock, AsyncMock, MagicMock

# Mock homeassistant before importing our modules
sys.modules['homeassistant'] = MagicMock()
sys.modules['homeassistant.helpers'] = MagicMock()
sys.modules['homeassistant.helpers.template'] = MagicMock()

# flake8: noqa: E402
import pytest
from datetime import datetime

from peaqevcore.common.spotprice.models.spotprice_dto import YourSourceDTO
from peaqevcore.common.spotprice.yoursource import YourSourceUpdater
from peaqevcore.common.spotprice.const import YOUR_SOURCE
from peaqevcore.common.models.peaq_system import PeaqSystem


class TestYourSourceDTO:
    """Test YourSource DTO transformations."""
    
    def test_transform_prices_24_hourly(self):
        """Test that 24 hourly prices pass through unchanged."""
        dto = YourSourceDTO()
        
        prices = [0.10 + i * 0.01 for i in range(24)]
        
        result = dto._transform_prices(prices)
        
        assert len(result) == 24
        assert result[0] == 0.10
        assert result[23] == 0.33
    
    def test_transform_prices_empty(self):
        """Test empty price list."""
        dto = YourSourceDTO()
        
        result = dto._transform_prices([])
        
        assert result == []
    
    def test_normalize_prices_cents(self):
        """Test cent detection and conversion."""
        dto = YourSourceDTO()
        
        # Prices in cents (average > 50)
        prices_cents = [100, 120, 150]
        
        result = dto._normalize_prices(prices_cents)
        
        assert result == [1.00, 1.20, 1.50]
    
    def test_normalize_prices_currency(self):
        """Test currency prices unchanged."""
        dto = YourSourceDTO()
        
        # Prices in currency (average < 50)
        prices_currency = [0.10, 0.12, 0.15]
        
        result = dto._normalize_prices(prices_currency)
        
        assert result == [0.10, 0.12, 0.15]
    
    def test_calculate_average_from_prices(self):
        """Test average calculation from price list."""
        dto = YourSourceDTO()
        
        prices = [0.10, 0.20, 0.30]
        
        result = dto._calculate_average({}, prices)
        
        assert abs(result - 0.20) < 0.001
    
    def test_calculate_average_from_attribute(self):
        """Test average extraction from attributes."""
        dto = YourSourceDTO()
        
        attributes = {"average": 0.25}
        
        result = dto._calculate_average(attributes, [])
        
        assert result == 0.25
    
    @pytest.mark.asyncio
    async def test_set_model_complete(self):
        """Test complete model creation."""
        dto = YourSourceDTO()
        
        sensor_data = {
            "attributes": {
                "today": [0.10] * 24,
                "tomorrow": [0.12] * 24,
                "average": 0.11
            }
        }
        
        dto.set_model(sensor_data, "Europe/Stockholm")
        
        assert len(dto.model.today) == 24
        assert len(dto.model.tomorrow) == 24
        assert dto.model.price_aware is True
        assert dto.model.average == 0.11


class TestYourSourceUpdater:
    """Test YourSource updater."""
    
    def test_init(self):
        """Test updater initialization."""
        updater = YourSourceUpdater()
        
        assert updater.source == YOUR_SOURCE
        assert updater.model is not None
    
    @pytest.mark.asyncio
    async def test_async_set_dto(self):
        """Test DTO setting."""
        updater = YourSourceUpdater()
        
        # Mock hub
        hub = Mock()
        hub.hours.timezone = "Europe/Stockholm"
        
        # Mock sensor data
        sensor_data = {
            "attributes": {
                "today": [0.15] * 24,
                "average": 0.15
            }
        }
        
        await updater.async_set_dto(hub, sensor_data)
        
        assert updater.model.price_aware is True
        assert len(updater.model.today) == 24
        assert updater.model.average == 0.15
```

**File**: `peaqevcore/tests/test_spotprice_factory_yoursource.py`

```python
"""Tests for SpotPriceFactory YourSource integration."""
import sys
from unittest.mock import MagicMock

# Mock homeassistant before importing our modules
sys.modules['homeassistant'] = MagicMock()
sys.modules['homeassistant.helpers'] = MagicMock()
sys.modules['homeassistant.helpers.template'] = MagicMock()

# flake8: noqa: E402
from peaqevcore.common.spotprice.spotprice_factory import SpotPriceFactory
from peaqevcore.common.spotprice.models.spotprice_type import SpotPriceType
from peaqevcore.common.spotprice.yoursource import YourSourceUpdater


class TestSpotPriceFactoryYourSource:
    """Test factory integration for YourSource."""
    
    def test_sources_includes_yoursource(self):
        """Verify YourSource is registered in factory sources."""
        assert SpotPriceType.YourSource in SpotPriceFactory.sources
        assert SpotPriceFactory.sources[SpotPriceType.YourSource] == YourSourceUpdater
    
    def test_yoursource_enum_value(self):
        """Verify YourSource enum has correct value."""
        assert SpotPriceType.YourSource.value == "your_source_name"
    
    def test_all_price_types_have_updaters(self):
        """Verify all price types have corresponding updaters."""
        for price_type in SpotPriceType:
            if price_type != SpotPriceType.Auto:
                assert price_type in SpotPriceFactory.sources
```

---

## Reference Implementation

### GE-Spot as Example

GE-Spot is the perfect reference because it handles complex scenarios:

**Challenges GE-Spot Solved**:
1. ✅ 96 15-minute intervals → 24 hourly aggregation
2. ✅ Automatic cent detection
3. ✅ Multiple attribute name variations
4. ✅ Handling None values in price arrays
5. ✅ Multiple sensor entity support

**Files to Review**:
```
peaqevcore/common/spotprice/
├── const.py                  # Line 3: GESPOT constant
├── gespot.py                 # 149 lines: Full updater
├── models/
│   ├── spotprice_type.py     # GESpot enum
│   └── spotprice_dto.py      # Lines 84-226: GESpotDTO class
└── spotprice_factory.py      # GE-Spot integration

peaqevcore/tests/
├── test_gespot.py            # 12 DTO/Updater tests
└── test_spotprice_factory_gespot.py  # 3 factory tests
```

**Commit History** (for learning):
1. `feat: Add GE-Spot electricity price integration support`
2. `test: Add comprehensive tests for GE-Spot integration`
3. `test: Fix GE-Spot tests to work without Home Assistant`
4. `chore: Code quality improvements and documentation`

---

## Testing Strategy

### Test Coverage Requirements

Aim for **100% coverage** of your new code:

**DTO Tests** (minimum 8 tests):
- ✅ Price transformation (various input formats)
- ✅ Empty/None handling
- ✅ Cent detection and conversion
- ✅ Average calculation (from attributes and prices)
- ✅ Complete model creation
- ✅ Edge cases (incomplete data, invalid formats)

**Updater Tests** (minimum 2 tests):
- ✅ Initialization
- ✅ DTO setting with mock data

**Factory Tests** (minimum 3 tests):
- ✅ Source registration
- ✅ Enum value correctness
- ✅ All sources have updaters

### Running Tests

```bash
# Run your tests
pytest peaqevcore/tests/test_yoursource.py -v

# Run with coverage
pytest peaqevcore/tests/test_yoursource.py --cov=peaqevcore.common.spotprice.yoursource --cov-report=term-missing

# Run all spotprice tests
pytest peaqevcore/tests/test_*spotprice* -v
```

### Mocking Home Assistant

Always mock Home Assistant modules:

```python
import sys
from unittest.mock import MagicMock

# Must be BEFORE importing peaqevcore modules
sys.modules['homeassistant'] = MagicMock()
sys.modules['homeassistant.helpers'] = MagicMock()
sys.modules['homeassistant.helpers.template'] = MagicMock()

# flake8: noqa: E402
# Now safe to import
from peaqevcore.common.spotprice.yoursource import YourSourceUpdater
```

---

## Code Review Checklist

Before submitting your PR, verify:

### Code Quality
- [ ] All flake8 checks pass: `flake8 peaqevcore/common/spotprice/yoursource.py --max-line-length=120`
- [ ] Type hints correct: `mypy peaqevcore/common/spotprice/yoursource.py --ignore-missing-imports`
- [ ] All tests pass: `pytest peaqevcore/tests/test_yoursource.py -v`
- [ ] No breaking changes to existing code
- [ ] Follows existing code style (review GE-Spot implementation)

### Completeness
- [ ] Constant added to `const.py`
- [ ] Enum added to `spotprice_type.py`
- [ ] DTO class created in `spotprice_dto.py`
- [ ] Updater class created in separate file
- [ ] Factory updated with detection logic
- [ ] Tests cover all new code paths
- [ ] Documentation added/updated

### Functionality
- [ ] Returns 24 hourly prices (list of floats)
- [ ] Handles missing tomorrow prices gracefully
- [ ] Detects and converts price units correctly
- [ ] price_aware set correctly
- [ ] Average calculated/extracted correctly
- [ ] Entity discovery works
- [ ] Observer pattern integration works

### Documentation
- [ ] Docstrings on all classes and methods
- [ ] Comments explain complex logic
- [ ] Update main README with new source
- [ ] Add entry to CHANGELOG
- [ ] Update SUPPORTED_SOURCES.md

---

## Common Pitfalls

### 1. Hardcoded Values

❌ **Wrong**:
```python
self.source = "your_source"
```

✅ **Correct**:
```python
from .const import YOUR_SOURCE
self.source = YOUR_SOURCE
```

### 2. Forgetting None Handling

❌ **Wrong**:
```python
average = sum(prices) / len(prices)  # Crashes if prices contains None
```

✅ **Correct**:
```python
valid_prices = [p for p in prices if p is not None]
if valid_prices:
    average = sum(valid_prices) / len(valid_prices)
```

### 3. Not Matching Entity Domain

❌ **Wrong**:
```python
YOUR_SOURCE = "YourSource"  # Uppercase won't match HA domain
```

✅ **Correct**:
```python
YOUR_SOURCE = "your_source"  # Match HA integration domain exactly
```

### 4. Missing Import in Factory

❌ **Wrong**:
```python
# Forgot to import YourSourceUpdater
sources = {
    SpotPriceType.YourSource: YourSourceUpdater,  # NameError!
}
```

✅ **Correct**:
```python
from .yoursource import YourSourceUpdater

sources = {
    SpotPriceType.YourSource: YourSourceUpdater,
}
```

### 5. Wrong Price Count

❌ **Wrong**:
```python
return prices[:23]  # Only 23 prices!
```

✅ **Correct**:
```python
return prices[:24]  # Always 24 hourly prices
```

### 6. Not Testing Edge Cases

❌ **Missing**:
```python
# Only test happy path
def test_normal_case():
    ...
```

✅ **Complete**:
```python
def test_normal_case(): ...
def test_empty_prices(): ...
def test_none_values(): ...
def test_missing_tomorrow(): ...
def test_invalid_format(): ...
```

---

## Example PR Description

When submitting your PR, use this template:

```markdown
# Add [YourSource] Integration Support

Adds support for the [YourSource] Home Assistant integration as a price source for peaqevcore.

## What is YourSource?

[Brief description of the integration and what regions/markets it covers]

## Changes Made

### Core Implementation
- Added `YOUR_SOURCE` constant in `const.py`
- Added `SpotPriceType.YourSource` enum
- Created `YourSourceDTO` for data transformation
- Created `YourSourceUpdater` class in `yoursource.py`
- Updated `SpotPriceFactory` with YourSource detection

### Testing
- Created comprehensive test suite (`test_yoursource.py`)
- 12 DTO transformation tests
- 2 updater tests
- 3 factory integration tests
- All 17 tests passing ✅

### Documentation
- Updated SUPPORTED_SOURCES.md
- Added entry to CHANGELOG.md
- Docstrings on all new classes/methods

## Data Transformation

[Explain how your source's data format is transformed]

Example:
- Input: [describe source format]
- Output: 24 hourly prices (standard format)

## Testing

```bash
pytest peaqevcore/tests/test_yoursource.py -v
# 17 passed in 0.05s ✅
```

## Checklist

- [x] Follows GE-Spot implementation pattern
- [x] Zero breaking changes
- [x] All tests passing
- [x] flake8 and mypy clean
- [x] Documentation updated
```

---

## Next Steps After Merge

1. **Release**: Maintainer creates new peaqevcore version
2. **Consumer Update**: Update hass-peaqev/hass-peaqhvac:
   - Add `"your_source"` to `after_dependencies`
   - Bump peaqevcore requirement to new version
3. **Announcement**: Announce new source support to users

---

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Issues**: Create an issue with `question` label
- **Examples**: Review GE-Spot implementation (PR #100)

---

## Related Documentation

- [Architecture Overview](../ARCHITECTURE.md)
- [Spot Price System](README.md)
- [GE-Spot Implementation](GE_SPOT.md)
- [Supported Price Sources](SUPPORTED_SOURCES.md)

---

**Good luck!** Following this guide and the GE-Spot example, you should be able to add a new price source in 4-8 hours. 🚀
