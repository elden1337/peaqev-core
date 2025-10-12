# GE-Spot Support Implementation Plan for peaqevcore & peaqhvac

**Version:** 1.0  
**Date:** October 12, 2025  
**Author:** Implementation Plan Generator  
**Objective:** Add GE-Spot electricity price integration support to peaqevcore library and update peaqhvac to use it

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Requirements Analysis](#requirements-analysis)
4. [Architecture Overview](#architecture-overview)
5. [Implementation Plan](#implementation-plan)
6. [Code Changes Detailed](#code-changes-detailed)
7. [Testing Strategy](#testing-strategy)
8. [Migration Path](#migration-path)
9. [Risk Assessment](#risk-assessment)
10. [Success Criteria](#success-criteria)

---

## 1. Executive Summary

### Goal
Add support for the GE-Spot (Global Electricity Spot Prices) integration as a price source in the peaqevcore library, following the existing architectural pattern of Nordpool and EnergiDataService, enabling both peaqhvac and peaqev to use GE-Spot for electricity pricing.

### Key Decisions
- **Location**: Implementation goes into `peaqevcore` (shared library) at `peaqevcore/common/spotprice/`
- **Pattern**: Follow existing Nordpool/EnergiDataService architecture
- **Compatibility**: Support GE-Spot v1.4.1+ with 15-minute interval data
- **Maintainability**: Clean, testable code following established patterns

### Estimated Effort
- **peaqevcore changes**: 4-6 hours (new files + factory updates)
- **peaqhvac changes**: 1-2 hours (manifest + minimal updates)
- **Testing**: 2-3 hours
- **Total**: ~8-11 hours

---

## 2. Current State Analysis

### 2.1 peaqevcore Architecture

#### Current Spotprice Structure
```
peaqevcore/common/spotprice/
├── __init__.py
├── const.py                    # Constants: NORDPOOL, ENERGIDATASERVICE
├── dynamic_top_price.py        # Price analytics
├── energidataservice.py        # EnergiDataService implementation
├── nordpool.py                 # Nordpool implementation
├── spotprice_factory.py        # Factory pattern for creating instances
├── spotpricebase.py            # Base class for all price sources
└── models/
    ├── average_type.py
    ├── dynamic_top_price_model.py
    ├── spotprice_dto.py        # DTOs: ISpotPriceDTO, NordpoolDTO, EnergiDataServiceDTO
    ├── spotprice_model.py
    └── spotprice_type.py       # Enum: NordPool, EnergidataService
```

#### Current Implementation Classes

**SpotPriceBase** (abstract base class):
- Properties: `is_initialized`, `currency`, `state`, `use_cent`, `source`, etc.
- Abstract methods: `async_set_dto()`, `setup()`
- Common methods: `async_update_spotprice()`, `async_update_set_prices()`

**NordPoolUpdater** (concrete implementation):
- Extends SpotPriceBase
- Uses `NordpoolDTO` for data transformation
- Discovery: Uses `template.integration_entities()` to find Nordpool sensors
- Validation: Tests sensor attributes (e.g., `additional_costs_current_hour`)

**EnergiDataServiceUpdater** (concrete implementation):
- Extends SpotPriceBase
- Uses `EnergiDataServiceDTO` for data transformation
- Direct sensor: Uses predefined sensor entity `sensor.energi_data_service`

**SpotPriceFactory**:
- `sources` dict mapping SpotPriceType to implementation classes
- `create()` method with auto-detection logic
- `test_connections()` for source selection

### 2.2 GE-Spot Integration Characteristics

#### Sensor Attributes (from documentation)
```python
sensor.gespot_current_price_<area>:
  attributes:
    today: [...]                      # List of prices for today (96 intervals)
    tomorrow: [...]                   # List of prices for tomorrow (96 intervals)
    tomorrow_valid: true/false        # Whether tomorrow's prices are available
    currency: "SEK" | "EUR" | etc.    # Currency code
    interval_prices: {...}            # Dict of time:price for today
    tomorrow_interval_prices: {...}   # Dict of time:price for tomorrow
    average: 1.23                     # Today's average price
    data_source: "nordpool" | etc.    # Active data source
    source_info: {...}                # Source health information
```

#### Key Differences from Nordpool
1. **Platform name**: `ge_spot` (vs `nordpool`)
2. **Interval granularity**: 15-minute intervals (96 per day) vs hourly (24 per day)
3. **Data format**: Similar to Nordpool but with more intervals
4. **Attributes**: Some differences in attribute names (e.g., `average` vs Nordpool's attribute structure)

#### Similarities with Nordpool
1. **Core attributes**: `today`, `tomorrow`, `tomorrow_valid`, `currency`
2. **Data structure**: Lists of price values
3. **Update cycle**: Daily updates with tomorrow's prices after ~13:00 CET

---

## 3. Requirements Analysis

### 3.1 Functional Requirements

#### FR1: GE-Spot Detection
- System shall automatically detect GE-Spot integration entities
- System shall use `template.integration_entities()` for discovery
- System shall support custom sensor entity override

#### FR2: Data Transformation
- System shall parse GE-Spot sensor attributes
- System shall extract: `today`, `tomorrow`, `tomorrow_valid`, `currency`, `average`
- System shall handle 15-minute interval data (96 data points)
- System shall convert to hourly data if needed for compatibility

#### FR3: Price Source Selection
- Factory shall include GE-Spot as a valid price source
- System shall support GE-Spot in priority/fallback logic
- User shall be able to explicitly select GE-Spot

#### FR4: Backward Compatibility
- Existing Nordpool and EnergiDataService functionality shall remain unchanged
- Default behavior without GE-Spot shall be preserved
- No breaking changes to existing APIs

### 3.2 Non-Functional Requirements

#### NFR1: Code Quality
- Code shall follow existing peaqevcore patterns
- Code shall have type hints where applicable
- Code shall include error handling
- Code shall include logging at appropriate levels

#### NFR2: Maintainability
- Implementation shall be modular and testable
- Documentation shall be clear and complete
- Code shall follow DRY (Don't Repeat Yourself) principle

#### NFR3: Performance
- No significant performance degradation
- Efficient entity discovery
- Minimal memory overhead

---

## 4. Architecture Overview

### 4.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    peaqhvac / peaqev                        │
│  (Integration Layer - Uses peaqevcore for price data)       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   SpotPriceFactory                          │
│  • create() - Factory method                                │
│  • test_connections() - Source detection                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        │             │             │              │
        ▼             ▼             ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Nordpool   │ │ EnergiData  │ │  GE-Spot    │ │   Future    │
│  Updater    │ │  Service    │ │  Updater    │ │   Sources   │
│             │ │  Updater    │ │   (NEW)     │ │             │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────────────┘
       │               │               │
       │               │               │
       └───────────────┴───────────────┴─────────────┐
                                                      ▼
                                        ┌──────────────────────┐
                                        │   SpotPriceBase      │
                                        │  (Abstract Base)     │
                                        └──────────────────────┘
                                                      │
                                        ┌─────────────┴──────────────┐
                                        │                            │
                                        ▼                            ▼
                              ┌──────────────────┐      ┌──────────────────┐
                              │  NordpoolDTO     │      │  GESpotDTO       │
                              │  (Transform)     │      │  (Transform)     │
                              └──────────────────┘      └──────────────────┘
                                        │                            │
                                        └─────────────┬──────────────┘
                                                      ▼
                                        ┌──────────────────────┐
                                        │  ISpotPriceDTO       │
                                        │  (Interface)         │
                                        └──────────────────────┘
```

### 4.2 Data Flow

```
1. Factory Creation
   SpotPriceFactory.create() 
   └─> test_connections()
       └─> Check for GE-Spot entities
           └─> Return SpotPriceType.GESpot if found

2. GE-Spot Initialization
   GESpotUpdater.__init__()
   └─> super().__init__(source="ge_spot")
   └─> setup()
       └─> Find GE-Spot entities
       └─> Validate entity
       └─> Initialize update

3. Data Update Flow
   async_update_spotprice()
   └─> Get entity state
   └─> async_set_dto()
       └─> Create GESpotDTO
       └─> Parse attributes
       └─> async_update_set_prices()
           └─> Update model
           └─> Broadcast events
```

---

## 5. Implementation Plan

### Phase 1: peaqevcore Changes (Core Implementation)

#### Step 1.1: Update Constants
**File**: `peaqevcore/common/spotprice/const.py`

**Changes**:
```python
# Add GE-Spot constant
NORDPOOL = "nordpool"
ENERGIDATASERVICE = "energidataservice"
GESPOT = "ge_spot"  # NEW
ENERGIDATASERVICE_SENSOR = "sensor.energi_data_service"
AVERAGE_MAX_LEN = 31
```

**Rationale**: Follow existing naming convention, use integration domain name

---

#### Step 1.2: Create GE-Spot DTO
**File**: `peaqevcore/common/spotprice/models/spotprice_dto.py`

**Changes**: Add new `GESpotDTO` class

**Implementation**:
```python
@dataclass
class GESpotDTO(ISpotPriceDTO):
    """
    Data Transfer Object for GE-Spot integration.
    
    GE-Spot provides 15-minute interval data (96 data points per day).
    This DTO handles the transformation to the expected format.
    """
    
    def _set_price_in_cent(self, ret) -> bool:
        """
        GE-Spot uses display format setting, similar to Nordpool's price_in_cent.
        Check for 'use_cent' or similar attribute.
        """
        # GE-Spot may use different attribute names based on display format
        return bool(ret.attributes.get("use_cent", False)) or \
               bool(ret.attributes.get("price_in_cent", False))

    def _set_average(self, ret) -> float:
        """
        Extract average price from GE-Spot attributes.
        GE-Spot provides 'average' attribute directly.
        """
        try:
            # GE-Spot has direct average attribute
            avg = ret.attributes.get("average", None)
            if avg is not None:
                return float(avg)
            
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
        """
        Determine the date for which the prices are valid.
        GE-Spot should have consistent timezone handling.
        """
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
        """
        Override to handle GE-Spot specific data parsing.
        GE-Spot has 96 intervals per day (15-minute intervals).
        We may need to aggregate to hourly for compatibility.
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
        """
        Aggregate 15-minute intervals to hourly data.
        
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
```

**Rationale**: 
- Handles GE-Spot's 15-minute interval data
- Aggregates to hourly for compatibility with existing systems
- Follows existing DTO pattern
- Robust error handling

---

#### Step 1.3: Create GE-Spot Updater
**File**: `peaqevcore/common/spotprice/gespot.py` (NEW)

**Implementation**:
```python
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
    """
    GE-Spot price updater.
    
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
        """
        Set data transfer object from sensor state.
        
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
        """
        Set up the GE-Spot integration.
        
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
        """
        Configure the entity and start price updates.
        
        Args:
            entity: Entity ID of the GE-Spot sensor
        """
        self.model.entity = entity
        _LOGGER.debug(
            f"GE-Spot has been set up and is ready to use with {self.entity}"
        )
        asyncio.run_coroutine_threadsafe(
            self.async_update_spotprice(initial=True),
            self.state_machine.loop,
        )
```

**Rationale**:
- Follows exact pattern of `nordpool.py`
- Simpler setup logic (no multi-sensor testing needed for GE-Spot)
- Clear logging for debugging
- Proper error handling

---

#### Step 1.4: Update SpotPriceType Enum
**File**: `peaqevcore/common/spotprice/models/spotprice_type.py`

**Changes**:
```python
from enum import Enum

from peaqevcore.common.spotprice.const import NORDPOOL, ENERGIDATASERVICE, GESPOT


class SpotPriceType(Enum):
    NordPool = NORDPOOL
    EnergidataService = ENERGIDATASERVICE
    GESpot = GESPOT  # NEW
    Auto = 'Auto'  # Keep existing Auto if present
```

---

#### Step 1.5: Update SpotPriceFactory
**File**: `peaqevcore/common/spotprice/spotprice_factory.py`

**Changes**:
```python
import logging

from peaqevcore.common.spotprice.const import *
from peaqevcore.common.spotprice.energidataservice import EnergiDataServiceUpdater
from peaqevcore.common.spotprice.gespot import GESpotUpdater  # NEW
from peaqevcore.common.spotprice.models.spotprice_type import SpotPriceType
from peaqevcore.common.spotprice.nordpool import NordPoolUpdater
from peaqevcore.common.spotprice.spotpricebase import SpotPriceBase
from peaqevcore.common.models.peaq_system import PeaqSystem

_LOGGER = logging.getLogger(__name__)


class SpotPriceFactory:

    sources = {
        SpotPriceType.NordPool: NordPoolUpdater,
        SpotPriceType.EnergidataService: EnergiDataServiceUpdater,
        SpotPriceType.GESpot: GESpotUpdater  # NEW
    }

    @staticmethod
    def create(
        hub, 
        observer, 
        system: PeaqSystem,
        test: bool = False, 
        is_active: bool = False,
        custom_sensor: str = None,
        spotprice_type: SpotPriceType = SpotPriceType.NordPool
    ) -> SpotPriceBase:
        if test:
            return NordPoolUpdater(hub, observer, system, test)
        source = SpotPriceFactory.test_connections(
            hub.state_machine, spotprice_type, system, custom_sensor
        )
        return SpotPriceFactory.sources[source](
            hub, observer, system, test, is_active, custom_sensor
        )

    @staticmethod
    def test_connections(
        hass,
        spotprice_type: SpotPriceType,
        system: PeaqSystem,
        custom_sensor: str = None
    ) -> SpotPriceType:
        """
        Test which price source is available and should be used.
        
        Priority order:
        1. Explicit spotprice_type if not Auto
        2. GE-Spot if entities found
        3. EnergiDataService if sensor exists
        4. Nordpool as fallback
        
        Args:
            hass: Home Assistant instance
            spotprice_type: Requested price source type
            system: PeaqSystem identifier
            custom_sensor: Optional custom sensor entity ID
            
        Returns:
            SpotPriceType to use
        """
        # If explicitly set to Nordpool from peaqev, honor it
        if spotprice_type == SpotPriceType.NordPool and system == PeaqSystem.PeaqEv:
            return SpotPriceType.NordPool
        
        # Check for GE-Spot (higher priority than other auto-detected sources)
        import homeassistant.helpers.template as template
        try:
            gespot_entities = template.integration_entities(hass, GESPOT)
            if len(list(gespot_entities)) > 0:
                _LOGGER.info("GE-Spot integration detected, using it for spot prices")
                return SpotPriceType.GESpot
        except Exception as e:
            _LOGGER.debug(f"GE-Spot not available: {e}")
        
        # Check for EnergiDataService
        sensor = hass.states.get(ENERGIDATASERVICE_SENSOR)
        if sensor or (custom_sensor and custom_sensor == ENERGIDATASERVICE_SENSOR):
            return SpotPriceType.EnergidataService
        
        # Fallback to Nordpool
        return SpotPriceType.NordPool
```

**Rationale**:
- Adds GE-Spot to auto-detection logic
- GE-Spot has priority over EnergiDataService (more universal)
- Maintains backward compatibility
- Clear logging

---

### Phase 2: peaqhvac Changes (Integration Layer)

#### Step 2.1: Update Manifest
**File**: `custom_components/peaqhvac/manifest.json`

**Changes**:
```json
{
    "domain": "peaqhvac",
    "name": "peaqhvac",
    "after_dependencies": [
      "myuplink",
      "nordpool",
      "energidataservice",
      "ge_spot",
      "peaqev",
      "met"
    ],
    "codeowners": [
      "@elden1337"
    ],
    "config_flow": true,
    "dependencies": [
      "recorder"
    ],
    "documentation": "https://github.com/elden1337/hass-peaqhvac",
    "integration_type": "hub",
    "iot_class": "calculated",
    "issue_tracker": "https://github.com/elden1337/hass-peaqhvac/issues",
    "requirements": [
      "peaqevcore==19.11.3"
    ],
    "version": "3.1.10"
  }
```

**Note**: Version of peaqevcore will need to be updated to the version that includes GE-Spot support

**Rationale**:
- Declares GE-Spot as optional dependency
- Ensures proper initialization order
- Documents supported integrations

---

#### Step 2.2: Verify Hub Integration (No Changes Needed)
**File**: `custom_components/peaqhvac/service/hub/hub.py`

**Analysis**: No changes needed if the hub already uses `SpotPriceFactory.create()`. The factory will automatically detect and use GE-Spot.

**Verification Point**: Check that hub initialization uses the factory pattern:
```python
self.spotprice = SpotPriceFactory.create(
    hub=self,
    observer=self.observer,
    system=PeaqSystem.PeaqHvac,
    is_active=True,
    custom_sensor=custom_price_sensor
)
```

---

### Phase 3: Testing

#### Step 3.1: Unit Tests for peaqevcore

**File**: `peaqevcore/tests/test_gespot.py` (NEW)

**Implementation**:
```python
"""Tests for GE-Spot integration."""
import pytest
from datetime import date, datetime
from unittest.mock import Mock, MagicMock
from peaqevcore.common.spotprice.gespot import GESpotUpdater
from peaqevcore.common.spotprice.models.spotprice_dto import GESpotDTO
from peaqevcore.common.models.peaq_system import PeaqSystem


@pytest.fixture
def mock_hub():
    """Create a mock hub."""
    hub = Mock()
    hub.state_machine = Mock()
    hub.observer = Mock()
    hub.observer.async_broadcast = MagicMock()
    hub.async_update_prices = MagicMock()
    return hub


@pytest.fixture
def mock_observer():
    """Create a mock observer."""
    observer = Mock()
    observer.async_broadcast = MagicMock()
    return observer


@pytest.fixture
def sample_gespot_state():
    """Create a sample GE-Spot state object."""
    state = Mock()
    state.state = 1.234
    state.attributes = {
        "today": [0.5 + i * 0.01 for i in range(96)],  # 96 intervals
        "tomorrow": [0.6 + i * 0.01 for i in range(96)],  # 96 intervals
        "tomorrow_valid": True,
        "currency": "SEK",
        "average": 0.75,
        "interval_prices": {f"{h:02d}:{m:02d}": 0.5 for h in range(24) for m in [0, 15, 30, 45]},
    }
    return state


class TestGESpotDTO:
    """Test GE-Spot DTO."""
    
    @pytest.mark.asyncio
    async def test_aggregate_to_hourly_96_intervals(self):
        """Test aggregation of 96 15-minute intervals to 24 hourly values."""
        dto = GESpotDTO()
        
        # Create 96 intervals with predictable values
        intervals_96 = [float(i) for i in range(96)]
        
        result = dto._aggregate_to_hourly(intervals_96)
        
        assert len(result) == 24
        # First hour average: (0+1+2+3)/4 = 1.5
        assert result[0] == 1.5
        # Second hour average: (4+5+6+7)/4 = 5.5
        assert result[1] == 5.5
    
    @pytest.mark.asyncio
    async def test_aggregate_to_hourly_24_intervals(self):
        """Test that 24 intervals are returned as-is."""
        dto = GESpotDTO()
        
        intervals_24 = [float(i) for i in range(24)]
        result = dto._aggregate_to_hourly(intervals_24)
        
        assert len(result) == 24
        assert result == intervals_24
    
    @pytest.mark.asyncio
    async def test_set_model_from_state(self, sample_gespot_state):
        """Test DTO model creation from GE-Spot state."""
        dto = GESpotDTO()
        await dto.set_model(sample_gespot_state)
        
        assert len(dto.today) == 24  # Aggregated to hourly
        assert len(dto.tomorrow) == 24  # Aggregated to hourly
        assert dto.tomorrow_valid is True
        assert dto.currency == "SEK"
        assert dto.average == 0.75
        assert dto.state == 1.234


class TestGESpotUpdater:
    """Test GE-Spot updater."""
    
    def test_initialization(self, mock_hub, mock_observer):
        """Test GE-Spot updater initialization."""
        updater = GESpotUpdater(
            hub=mock_hub,
            observer=mock_observer,
            system=PeaqSystem.PeaqHvac,
            test=True
        )
        
        assert updater.source == "ge_spot"
        assert updater.model.source == "ge_spot"
    
    @pytest.mark.asyncio
    async def test_async_set_dto(self, mock_hub, mock_observer, sample_gespot_state):
        """Test DTO setting and price updates."""
        updater = GESpotUpdater(
            hub=mock_hub,
            observer=mock_observer,
            system=PeaqSystem.PeaqHvac,
            test=True
        )
        
        # Mock the update method to return True
        updater.async_update_set_prices = MagicMock(return_value=True)
        
        await updater.async_set_dto(sample_gespot_state, initial=True)
        
        # Verify broadcasts were called
        assert updater._is_initialized is True
```

**Rationale**: Comprehensive testing of new functionality

---

#### Step 3.2: Integration Tests

**File**: `peaqevcore/tests/test_spotprice_factory_gespot.py` (NEW)

**Implementation**:
```python
"""Test SpotPriceFactory with GE-Spot."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from peaqevcore.common.spotprice.spotprice_factory import SpotPriceFactory
from peaqevcore.common.spotprice.models.spotprice_type import SpotPriceType
from peaqevcore.common.spotprice.gespot import GESpotUpdater
from peaqevcore.common.models.peaq_system import PeaqSystem


@pytest.fixture
def mock_hass_with_gespot():
    """Create mock Home Assistant with GE-Spot entities."""
    hass = Mock()
    hass.states = Mock()
    
    # Mock GE-Spot entity
    gespot_sensor = Mock()
    gespot_sensor.entity_id = "sensor.gespot_current_price_se4"
    
    return hass


class TestSpotPriceFactoryGESpot:
    """Test factory with GE-Spot support."""
    
    @patch('peaqevcore.common.spotprice.spotprice_factory.template')
    def test_detect_gespot(self, mock_template, mock_hass_with_gespot):
        """Test that factory detects GE-Spot when available."""
        # Mock integration_entities to return GE-Spot entities
        mock_template.integration_entities.return_value = [
            "sensor.gespot_current_price_se4"
        ]
        
        result = SpotPriceFactory.test_connections(
            mock_hass_with_gespot,
            SpotPriceType.NordPool,
            PeaqSystem.PeaqHvac
        )
        
        assert result == SpotPriceType.GESpot
    
    @patch('peaqevcore.common.spotprice.spotprice_factory.template')
    def test_create_gespot_updater(self, mock_template):
        """Test creation of GE-Spot updater."""
        mock_hub = Mock()
        mock_hub.state_machine = Mock()
        mock_observer = Mock()
        
        mock_template.integration_entities.return_value = [
            "sensor.gespot_current_price_se4"
        ]
        
        updater = SpotPriceFactory.create(
            hub=mock_hub,
            observer=mock_observer,
            system=PeaqSystem.PeaqHvac,
            test=False,
            is_active=False,
            spotprice_type=SpotPriceType.GESpot
        )
        
        assert isinstance(updater, GESpotUpdater)
        assert updater.source == "ge_spot"
```

---

## 6. Code Changes Detailed

### 6.1 Files to Create (peaqevcore)

1. **`peaqevcore/common/spotprice/gespot.py`**
   - Size: ~150 lines
   - Complexity: Medium
   - Dependencies: SpotPriceBase, GESpotDTO, GESPOT constant
   
2. **`peaqevcore/tests/test_gespot.py`**
   - Size: ~200 lines
   - Complexity: Medium
   - Purpose: Unit tests for GE-Spot functionality

3. **`peaqevcore/tests/test_spotprice_factory_gespot.py`**
   - Size: ~100 lines
   - Complexity: Low
   - Purpose: Factory integration tests

### 6.2 Files to Modify (peaqevcore)

1. **`peaqevcore/common/spotprice/const.py`**
   - Lines changed: +1
   - Risk: Very Low
   
2. **`peaqevcore/common/spotprice/models/spotprice_dto.py`**
   - Lines changed: +120
   - Risk: Low (new class, doesn't affect existing)
   
3. **`peaqevcore/common/spotprice/models/spotprice_type.py`**
   - Lines changed: +2
   - Risk: Very Low
   
4. **`peaqevcore/common/spotprice/spotprice_factory.py`**
   - Lines changed: +25
   - Risk: Low (backwards compatible additions)

### 6.3 Files to Modify (peaqhvac)

1. **`custom_components/peaqhvac/manifest.json`**
   - Lines changed: +2 (add "ge_spot" to after_dependencies, bump version)
   - Risk: Very Low

### 6.4 Total Code Impact

- **New files**: 3 (all in peaqevcore)
- **Modified files**: 5 (4 in peaqevcore, 1 in peaqhvac)
- **Total new lines**: ~470
- **Total modified lines**: ~30
- **Test coverage**: ~300 lines of tests

---

## 7. Testing Strategy

### 7.1 Unit Testing

**Scope**:
- GESpotDTO data transformation
- Interval aggregation (96 → 24)
- Error handling
- Attribute parsing

**Tools**: pytest, pytest-asyncio

**Coverage Target**: >90% for new code

### 7.2 Integration Testing

**Scope**:
- Factory detection logic
- Entity discovery
- End-to-end data flow
- Multi-source scenarios

**Mock Requirements**:
- Home Assistant state machine
- GE-Spot sensor entities
- Observer broadcasts

### 7.3 Manual Testing

**Test Cases**:

1. **TC1: Fresh Installation with GE-Spot**
   - Precondition: GE-Spot installed and configured
   - Steps: Install peaqhvac, configure
   - Expected: GE-Spot automatically detected and used

2. **TC2: Migration from Nordpool**
   - Precondition: peaqhvac using Nordpool
   - Steps: Install GE-Spot
   - Expected: Automatic switch to GE-Spot (higher priority)

3. **TC3: Custom Sensor Override**
   - Precondition: Multiple price integrations
   - Steps: Configure custom GE-Spot sensor
   - Expected: Specified sensor used

4. **TC4: Data Accuracy**
   - Precondition: GE-Spot active
   - Steps: Compare prices with GE-Spot UI
   - Expected: Prices match (within aggregation tolerance)

5. **TC5: Fallback Behavior**
   - Precondition: GE-Spot fails/unavailable
   - Steps: Monitor logs, check prices
   - Expected: Graceful fallback to Nordpool

### 7.4 Regression Testing

**Scope**: Ensure existing functionality unchanged
- Nordpool still works
- EnergiDataService still works
- Factory auto-detection for existing sources
- No performance degradation

---

## 8. Migration Path

### 8.1 For peaqevcore

**Release Process**:
1. Merge GE-Spot support to main branch
2. Tag new version (e.g., v19.11.3)
3. Publish to PyPI
4. Update changelog

**Versioning**: Minor version bump (19.11.2 → 19.11.3)
- Reason: New feature, backward compatible

### 8.2 For peaqhvac

**Update Steps**:
1. Update manifest.json dependencies
2. Update version number
3. Test with new peaqevcore version
4. Create release notes

**Rollback Plan**:
- Revert to peaqevcore 19.11.2
- Remove "ge_spot" from after_dependencies
- No code changes needed

### 8.3 User Migration

**User Actions**: None required
- Automatic detection
- Seamless integration
- Opt-out via custom sensor configuration

**Communication**:
- Release notes mention GE-Spot support
- Documentation update
- Example configurations

---

## 9. Risk Assessment

### 9.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Interval aggregation errors | Low | Medium | Comprehensive testing, validation logic |
| GE-Spot attribute changes | Medium | Low | Robust parsing, fallbacks, version checking |
| Performance with 96 intervals | Low | Low | Efficient aggregation, minimal overhead |
| Breaking existing integrations | Very Low | High | Extensive regression testing |
| Factory detection conflicts | Low | Medium | Clear priority order, logging |

### 9.2 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| User confusion (multiple sources) | Medium | Low | Clear documentation, auto-detection |
| GE-Spot API instability | Low | Medium | Fallback to other sources |
| Version mismatches | Low | Medium | Explicit version requirements |

### 9.3 Mitigation Strategies

1. **Comprehensive Testing**: Unit, integration, and manual tests
2. **Backward Compatibility**: All changes are additive
3. **Error Handling**: Graceful degradation and clear logging
4. **Documentation**: Clear upgrade path and configuration guide
5. **Rollback Plan**: Easy reversion to previous version

---

## 10. Success Criteria

### 10.1 Functional Success

- [ ] GE-Spot entities automatically detected
- [ ] Price data correctly parsed and aggregated
- [ ] Integration works with peaqhvac and peaqev
- [ ] Fallback logic works correctly
- [ ] Custom sensor override works
- [ ] All existing tests pass
- [ ] New tests achieve >90% coverage

### 10.2 Non-Functional Success

- [ ] No performance degradation
- [ ] Memory footprint unchanged
- [ ] Logs are clear and helpful
- [ ] Code follows project conventions
- [ ] Documentation is complete

### 10.3 User Success

- [ ] Zero-configuration setup for users with GE-Spot
- [ ] Clear error messages if issues occur
- [ ] Smooth migration from other sources
- [ ] Positive community feedback

---

## Appendix A: File Checklist

### peaqevcore Repository

**New Files**:
- [ ] `peaqevcore/common/spotprice/gespot.py`
- [ ] `peaqevcore/tests/test_gespot.py`
- [ ] `peaqevcore/tests/test_spotprice_factory_gespot.py`

**Modified Files**:
- [ ] `peaqevcore/common/spotprice/const.py`
- [ ] `peaqevcore/common/spotprice/models/spotprice_dto.py`
- [ ] `peaqevcore/common/spotprice/models/spotprice_type.py`
- [ ] `peaqevcore/common/spotprice/spotprice_factory.py`

### peaqhvac Repository

**Modified Files**:
- [ ] `custom_components/peaqhvac/manifest.json`

**Verification Points**:
- [ ] Hub uses SpotPriceFactory correctly
- [ ] No hardcoded Nordpool references to change

---

## Appendix B: Code Review Checklist

**Architecture**:
- [ ] Follows existing patterns
- [ ] Proper separation of concerns
- [ ] No tight coupling

**Code Quality**:
- [ ] Type hints used appropriately
- [ ] Error handling comprehensive
- [ ] Logging at correct levels
- [ ] No code duplication

**Testing**:
- [ ] Unit tests for all new functions
- [ ] Integration tests for factory
- [ ] Edge cases covered
- [ ] Mocking appropriate

**Documentation**:
- [ ] Docstrings complete
- [ ] Comments where needed
- [ ] README updated
- [ ] Changelog updated

**Compatibility**:
- [ ] Backward compatible
- [ ] No breaking changes
- [ ] Version requirements clear

---

## Appendix C: Timeline Estimate

**Day 1: peaqevcore Implementation (6-7 hours)**
- Hour 1-2: Create gespot.py and GESpotDTO
- Hour 3-4: Update factory and enum
- Hour 5-6: Write unit tests
- Hour 7: Integration tests

**Day 2: Testing & peaqhvac Update (3-4 hours)**
- Hour 1-2: Manual testing with real GE-Spot
- Hour 3: Update peaqhvac manifest
- Hour 4: End-to-end testing

**Day 3: Documentation & Release (2 hours)**
- Hour 1: Documentation updates
- Hour 2: Release preparation

**Total: 11-13 hours** (including buffer)

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-12 | Implementation Team | Initial comprehensive plan |

---

**END OF IMPLEMENTATION PLAN**
