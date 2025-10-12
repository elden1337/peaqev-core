# peaqevcore Architecture Overview

**Audience**: Integration developers and core contributors  
**Last Updated**: October 2025  
**Version**: 19.12.0+

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Spot Price Architecture](#spot-price-architecture)
3. [Component Hierarchy](#component-hierarchy)
4. [Data Flow](#data-flow)
5. [Extension Points](#extension-points)

---

## System Overview

peaqevcore is a **shared library** that provides electricity price management services for Home Assistant integrations. It's designed to be price-source agnostic, allowing multiple electricity price integrations to coexist.

### High-Level Architecture

```mermaid
graph TB
    subgraph HA["Home Assistant"]
        Nordpool["Nordpool<br/>Integration"]
        GESpot["GE-Spot<br/>Integration"]
        EDS["Energi Data<br/>Service"]
        Future["Future<br/>Source"]
    end
    
    subgraph Core["peaqevcore"]
        Factory["SpotPriceFactory<br/>• Auto-detects sources<br/>• Selects by priority<br/>• Creates updater"]
        
        subgraph Updaters["SpotPrice Updaters"]
            NordpoolUpd["Nordpool<br/>Updater"]
            GESpotUpd["GE-Spot<br/>Updater"]
            EDSUpd["Energi Data<br/>Updater"]
        end
        
        subgraph DTOs["DTO Layer"]
            DTOLayer["• Transform source data<br/>• Normalize format<br/>• Handle intervals"]
        end
        
        Model["Standardized Price Model<br/>• today: List[float] (24h)<br/>• tomorrow: List[float]<br/>• average: float<br/>• price_aware: bool"]
    end
    
    subgraph Consumers["Consumer Integrations"]
        PeaqEV["hass-peaqev<br/>(EV Charging)"]
        PeaqHVAC["hass-peaqhvac<br/>(HVAC)"]
    end
    
    Nordpool --> Factory
    GESpot --> Factory
    EDS --> Factory
    Future --> Factory
    
    Factory --> NordpoolUpd
    Factory --> GESpotUpd
    Factory --> EDSUpd
    
    NordpoolUpd --> DTOLayer
    GESpotUpd --> DTOLayer
    EDSUpd --> DTOLayer
    
    DTOLayer --> Model
    
    Model --> PeaqEV
    Model --> PeaqHVAC
    
    style Factory fill:#fff,stroke:#333,stroke-width:3px
    style Model fill:#fff,stroke:#333,stroke-width:3px
```

---

## Spot Price Architecture

### Core Components

#### 1. **SpotPriceFactory**
- **Location**: `peaqevcore/common/spotprice/spotprice_factory.py`
- **Responsibility**: Detect and instantiate the appropriate price updater
- **Key Method**: `test_connections(hass, spotprice_type, system, custom_sensor)`

**Detection Logic**:

```mermaid
flowchart TD
    Start([Factory.test_connections]) --> CheckGESpot{GE-Spot<br/>entities<br/>found?}
    CheckGESpot -->|Yes| ReturnGESpot[Return GESpotUpdater]
    CheckGESpot -->|No| CheckEDS{Energi Data<br/>Service<br/>entities?}
    CheckEDS -->|Yes| ReturnEDS[Return EDSUpdater]
    CheckEDS -->|No| CheckPeaqEv{Is PeaqEv<br/>system?}
    CheckPeaqEv -->|Yes| ReturnNordpool[Return NordpoolUpdater<br/>Legacy compatibility]
    CheckPeaqEv -->|No| ReturnNordpool
    
    ReturnGESpot --> End([Create Updater])
    ReturnEDS --> End
    ReturnNordpool --> End
    
    style ReturnGESpot fill:#fff,stroke:#333,stroke-width:2px
    style ReturnEDS fill:#fff,stroke:#333,stroke-width:2px
    style ReturnNordpool fill:#fff,stroke:#333,stroke-width:2px
```

#### 2. **SpotPriceUpdater** (Abstract Base)
- **Location**: `peaqevcore/common/spotprice/spotpricebase.py`
- **Implementations**:
  - `NordpoolUpdater` - Nordic countries
  - `EnergiDataServiceUpdater` - Denmark
  - `GESpotUpdater` - Multi-region (EU, Nordic, others)

**Common Interface**:
```python
class SpotPriceBase(ABC):
    async def async_update_spotprice()  # Get latest prices
    async def async_set_dto()            # Transform data via DTO
    async def setup()                    # Discover entities
```

#### 3. **SpotPriceDTO** (Data Transfer Object)
- **Location**: `peaqevcore/common/spotprice/models/spotprice_dto.py`
- **Implementations**:
  - `NordpoolDTO`
  - `EnergiDataServiceDTO`
  - `GESpotDTO`

**Responsibilities**:
- Parse source-specific data structures
- Transform intervals (e.g., 96 × 15-min → 24 × hourly)
- Detect price units (cents vs currency)
- Calculate averages
- Normalize to standard model

---

## Component Hierarchy

### Class Inheritance

```mermaid
classDiagram
    class SpotPriceBase {
        <<ABC>>
        +async_update_spotprice()
        +async_set_dto()
        +setup()
    }
    
    class ISpotPriceDTO {
        <<ABC>>
        +set_model()
        +_aggregate_to_hourly()
        +_set_price_in_cent()
        +_set_average()
    }
    
    class SpotPriceType {
        <<Enum>>
        Nordpool
        EnergidataService
        GESpot
        Auto
    }
    
    SpotPriceBase <|-- NordpoolUpdater
    SpotPriceBase <|-- EnergiDataServiceUpdater
    SpotPriceBase <|-- GESpotUpdater
    
    ISpotPriceDTO <|-- NordpoolDTO
    ISpotPriceDTO <|-- EnergiDataServiceDTO
    ISpotPriceDTO <|-- GESpotDTO
    
    NordpoolUpdater --> NordpoolDTO
    EnergiDataServiceUpdater --> EnergiDataServiceDTO
    GESpotUpdater --> GESpotDTO
```

### File Structure

```
peaqevcore/
├── common/
│   └── spotprice/
│       ├── const.py              # Constants (NORDPOOL, GESPOT, etc.)
│       ├── spotpricebase.py      # Abstract base class
│       ├── nordpool.py           # Nordpool implementation
│       ├── energidataservice.py  # EnergiDataService implementation
│       ├── gespot.py             # GE-Spot implementation
│       ├── spotprice_factory.py  # Factory for auto-detection
│       └── models/
│           ├── spotprice_type.py # Enum for price types
│           ├── spotprice_dto.py  # DTO implementations
│           └── spotprice_model.py# Data model
└── tests/
    ├── test_nordpool.py
    ├── test_energidataservice.py
    ├── test_gespot.py
    └── test_spotprice_factory_gespot.py
```

---

## Data Flow

### Typical Price Update Cycle

```mermaid
sequenceDiagram
    participant HA as Home Assistant<br/>Integration
    participant Obs as Observer Pattern
    participant Upd as SpotPriceUpdater
    participant DTO as DTO Layer
    participant Model as SpotPriceModel
    participant Consumer as PeaqEV/PeaqHVAC
    
    HA->>Obs: Update sensor<br/>(e.g., GE-Spot prices)
    Obs->>Upd: Trigger state change
    Upd->>Upd: async_update_spotprice()<br/>• Fetch sensor state<br/>• Extract attributes
    Upd->>DTO: async_set_dto()<br/>Pass sensor data
    DTO->>DTO: set_model()
    Note over DTO: • _aggregate_to_hourly()<br/>• _set_price_in_cent()<br/>• _set_average()<br/>• _set_affected_date()
    DTO->>Model: Create standardized model
    Note over Model: today: [24 prices]<br/>tomorrow: [24 prices]<br/>average: float<br/>price_aware: bool
    Model->>Consumer: Provide price data
    Consumer->>Consumer: Make optimization<br/>decisions
```

---

## Extension Points

### Adding a New Price Source

To add support for a new electricity price integration (like we did with GE-Spot):

**Step 1**: Add constant
```python
# peaqevcore/common/spotprice/const.py
YOUR_SOURCE = "your_source"
```

**Step 2**: Add enum
```python
# peaqevcore/common/spotprice/models/spotprice_type.py
class SpotPriceType(str, Enum):
    YourSource = YOUR_SOURCE
```

**Step 3**: Create DTO
```python
# peaqevcore/common/spotprice/models/spotprice_dto.py
class YourSourceDTO(ISpotPriceDTO):
    def set_model(self, ...):
        # Transform your source's data format
```

**Step 4**: Create Updater
```python
# peaqevcore/common/spotprice/yoursource.py
class YourSourceUpdater(SpotPriceBase):
    def __init__(self):
        super().__init__(source=YOUR_SOURCE)
    
    async def setup(self, ...):
        # Discover entities
    
    async def async_set_dto(self, ...):
        # Use YourSourceDTO
```

**Step 5**: Update Factory
```python
# peaqevcore/common/spotprice/spotprice_factory.py
from .yoursource import YourSourceUpdater

sources = {
    SpotPriceType.YourSource: YourSourceUpdater,
    # ... existing sources
}

def test_connections(...):
    # Add detection logic for your source
```

**Step 6**: Write Tests
```python
# peaqevcore/tests/test_yoursource.py
# - DTO transformation tests
# - Updater initialization tests
# - Factory integration tests
```

See [Adding a New Price Source](spotprice/ADDING_NEW_SOURCE.md) for detailed guide.

---

## Design Decisions

### Why Factory Pattern?

The `SpotPriceFactory` allows **automatic detection** of available price sources without requiring user configuration. Users just install the price integration they want, and peaqevcore automatically uses it.

### Why DTO Layer?

Different price integrations have different data formats:
- **Nordpool**: Hourly prices directly
- **GE-Spot**: 15-minute intervals (96 per day)
- **EnergiDataService**: Hourly with specific attributes

The DTO layer **normalizes** these differences into a standard format.

### Why Priority System?

When multiple price sources are available, the factory chooses based on:
1. **GE-Spot** (most flexible, multi-region)
2. **EnergiDataService** (Denmark-specific, official)
3. **Nordpool** (Nordic countries, well-established)

Exception: PeaqEv system prefers Nordpool for legacy compatibility.

---

## Performance Considerations

- **Lazy Loading**: Updaters only created when needed
- **Async Operations**: All price updates are async
- **Caching**: Price data cached until next update cycle
- **Observer Pattern**: Efficient state change detection

---

## Security & Privacy

- No external API calls from peaqevcore
- All data comes from local Home Assistant entities
- No personal data collected or transmitted
- Price data stays within Home Assistant

---

## Next Steps

- **For Integration Developers**: Read [Spot Price System](spotprice/README.md)
- **For Adding New Sources**: Read [Adding a New Price Source](spotprice/ADDING_NEW_SOURCE.md)
- **For GE-Spot Details**: Read [GE-Spot Integration](spotprice/GE_SPOT.md)
