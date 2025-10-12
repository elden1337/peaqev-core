# GE-Spot Architecture Diagrams

## Current State (Before GE-Spot)

```
┌──────────────────────────────────────────────────────────────┐
│                     Home Assistant                           │
│  ┌────────────────┐  ┌────────────────┐                     │
│  │   Nordpool     │  │ EnergiData     │                     │
│  │  Integration   │  │   Service      │                     │
│  └────────┬───────┘  └────────┬───────┘                     │
│           │                    │                             │
└───────────┼────────────────────┼─────────────────────────────┘
            │                    │
            │                    │
┌───────────▼────────────────────▼─────────────────────────────┐
│                     peaqevcore                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           SpotPriceFactory                           │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  test_connections()                          │   │   │
│  │  │  • Check for EnergiDataService               │   │   │
│  │  │  • Fallback to Nordpool                      │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                      │   │
│  │  sources = {                                         │   │
│  │    NordPool: NordPoolUpdater,                       │   │
│  │    EnergidataService: EnergiDataServiceUpdater      │   │
│  │  }                                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│           │                    │                             │
│           │                    │                             │
│  ┌────────▼──────┐    ┌───────▼──────────┐                 │
│  │ NordPool      │    │ EnergiData       │                 │
│  │ Updater       │    │ Service Updater  │                 │
│  └────────┬──────┘    └───────┬──────────┘                 │
│           │                    │                             │
│  ┌────────▼──────┐    ┌───────▼──────────┐                 │
│  │ NordpoolDTO   │    │EnergiDataDTO     │                 │
│  └───────────────┘    └──────────────────┘                 │
└──────────────────────────────────────────────────────────────┘
            │                    │
            │                    │
┌───────────▼────────────────────▼─────────────────────────────┐
│                  peaqhvac / peaqev                           │
│  Uses price data for:                                        │
│  • HVAC scheduling                                           │
│  • Cost optimization                                         │
│  • Demand management                                         │
└──────────────────────────────────────────────────────────────┘
```

## Future State (With GE-Spot)

```
┌──────────────────────────────────────────────────────────────┐
│                     Home Assistant                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Nordpool  │  │ EnergiData │  │  GE-Spot   │ ◄── NEW!  │
│  │Integration │  │  Service   │  │Integration │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
│        │               │               │                     │
└────────┼───────────────┼───────────────┼─────────────────────┘
         │               │               │
         │               │               │
┌────────▼───────────────▼───────────────▼─────────────────────┐
│                     peaqevcore                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           SpotPriceFactory                           │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  test_connections() - ENHANCED               │   │   │
│  │  │  1. Check for GE-Spot          ◄── NEW!     │   │   │
│  │  │  2. Check for EnergiDataService              │   │   │
│  │  │  3. Fallback to Nordpool                     │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                      │   │
│  │  sources = {                                         │   │
│  │    NordPool: NordPoolUpdater,                       │   │
│  │    EnergidataService: EnergiDataServiceUpdater,     │   │
│  │    GESpot: GESpotUpdater  ◄── NEW!                 │   │
│  │  }                                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│         │               │               │                    │
│         │               │               │                    │
│  ┌──────▼─────┐  ┌──────▼──────┐  ┌────▼────────┐          │
│  │ NordPool   │  │ EnergiData  │  │  GESpot     │ ◄── NEW! │
│  │  Updater   │  │   Service   │  │  Updater    │          │
│  │            │  │   Updater   │  │             │          │
│  └──────┬─────┘  └──────┬──────┘  └────┬────────┘          │
│         │               │               │                    │
│  ┌──────▼─────┐  ┌──────▼──────┐  ┌────▼────────┐          │
│  │ Nordpool   │  │ EnergiData  │  │  GESpot     │ ◄── NEW! │
│  │    DTO     │  │     DTO     │  │    DTO      │          │
│  └────────────┘  └─────────────┘  └─────────────┘          │
│                                                              │
│  All share common base: SpotPriceBase                       │
│  All implement: async_set_dto(), setup()                    │
└──────────────────────────────────────────────────────────────┘
         │               │               │
         │               │               │
┌────────▼───────────────▼───────────────▼─────────────────────┐
│                  peaqhvac / peaqev                           │
│  Uses price data for:                                        │
│  • HVAC scheduling                                           │
│  • Cost optimization                                         │
│  • Demand management                                         │
│  ✓ No changes needed - uses factory automatically!           │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow - GE-Spot Integration

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Entity Discovery                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SpotPriceFactory.test_connections()                 │   │
│  │   ↓                                                  │   │
│  │ template.integration_entities(hass, "ge_spot")      │   │
│  │   ↓                                                  │   │
│  │ Found: ["sensor.gespot_current_price_se4"]          │   │
│  │   ↓                                                  │   │
│  │ Return: SpotPriceType.GESpot                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Updater Creation                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SpotPriceFactory.create()                           │   │
│  │   ↓                                                  │   │
│  │ sources[SpotPriceType.GESpot]                       │   │
│  │   ↓                                                  │   │
│  │ GESpotUpdater(hub, observer, system, ...)           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Initial Setup                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ GESpotUpdater.setup()                               │   │
│  │   ↓                                                  │   │
│  │ Find sensor: "sensor.gespot_current_price_se4"      │   │
│  │   ↓                                                  │   │
│  │ _setup_set_entity()                                 │   │
│  │   ↓                                                  │   │
│  │ async_update_spotprice(initial=True)                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Data Retrieval                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ state = hass.states.get("sensor.gespot_current...")│   │
│  │                                                      │   │
│  │ state.attributes = {                                │   │
│  │   "today": [0.5, 0.51, ..., 1.45],  # 96 values    │   │
│  │   "tomorrow": [0.6, 0.61, ..., 1.55], # 96 values  │   │
│  │   "tomorrow_valid": True,                           │   │
│  │   "currency": "SEK",                                │   │
│  │   "average": 0.75                                   │   │
│  │ }                                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Data Transformation                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ async_set_dto(state)                                │   │
│  │   ↓                                                  │   │
│  │ dto = GESpotDTO()                                   │   │
│  │ await dto.set_model(state)                          │   │
│  │   ↓                                                  │   │
│  │ dto._aggregate_to_hourly([96 values])               │   │
│  │   • Take intervals 0-3: avg → hour 0               │   │
│  │   • Take intervals 4-7: avg → hour 1               │   │
│  │   • ...                                             │   │
│  │   • Take intervals 92-95: avg → hour 23            │   │
│  │   ↓                                                  │   │
│  │ Result: 24 hourly prices                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Model Update                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ async_update_set_prices(dto)                        │   │
│  │   ↓                                                  │   │
│  │ model.prices = [24 hourly values]                   │   │
│  │ model.prices_tomorrow = [24 hourly values]          │   │
│  │ model.currency = "SEK"                              │   │
│  │ model.tomorrow_valid = True                         │   │
│  │   ↓                                                  │   │
│  │ observer.broadcast(SpotpriceInitialized)            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 7: Usage in peaqhvac                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ hub.spotprice.model.prices                          │   │
│  │   → [24 hourly prices]                              │   │
│  │                                                      │   │
│  │ Used for:                                            │   │
│  │ • Scheduling HVAC operations                         │   │
│  │ • Cost calculations                                  │   │
│  │ • Demand predictions                                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## GE-Spot Interval Aggregation

```
GE-Spot 15-minute intervals (96 per day):
┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬─ ... ─┬──┬──┬──┬──┐
│00│15│30│45│00│15│30│45│00│15│30│45│       │30│45│00│15│
│:0│:0│:0│:0│:1│:1│:1│:1│:2│:2│:2│:2│       │:2│:2│:2│:2│
│0 │0 │0 │0 │5 │5 │5 │5 │0 │0 │0 │0 │ ...   │2 │2 │3 │3 │
└──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴─ ... ─┴──┴──┴──┴──┘
0.50 0.51 0.52 0.53 0.54 ... (price values)
 │    │    │    │    │
 └────┴────┴────┘    │
        │             │
        ▼             ▼
   average(0.50, 0.51, 0.52, 0.53) = 0.515
        │
        │
        ▼
Aggregated hourly (24 per day):
┌────┬────┬────┬────┬────┬─ ... ─┬────┬────┐
│ 00 │ 01 │ 02 │ 03 │ 04 │       │ 22 │ 23 │
└────┴────┴────┴────┴────┴─ ... ─┴────┴────┘
 0.515 0.545 0.575 ...
 
 Hour 0: avg(intervals 0-3)   = 0.515
 Hour 1: avg(intervals 4-7)   = 0.545
 Hour 2: avg(intervals 8-11)  = 0.575
 ...
 Hour 23: avg(intervals 92-95) = 0.875
```

## Factory Auto-Detection Logic

```
┌────────────────────────────────────────────────────────┐
│ SpotPriceFactory.test_connections()                    │
└───────────────────┬────────────────────────────────────┘
                    ▼
        ┌───────────────────────────┐
        │ Explicit type specified?  │
        │ (e.g., NordPool from EV)  │
        └───────┬───────────────────┘
                │
        ┌───────▼────────┐
        │ YES            │ NO
        │                │
        ▼                ▼
┌───────────────┐  ┌──────────────────────────────┐
│ Return        │  │ Check for GE-Spot entities   │ ◄── NEW!
│ specified     │  │ template.integration_entities│
│ type          │  │ (hass, "ge_spot")            │
└───────────────┘  └──────────┬───────────────────┘
                              │
                   ┌──────────▼──────────┐
                   │ GE-Spot found?      │
                   └──────────┬──────────┘
                              │
                   ┌──────────▼────────┬──────────┐
                   │ YES               │ NO       │
                   │                   │          │
                   ▼                   ▼          
         ┌──────────────────┐  ┌──────────────────────────┐
         │ Return           │  │ Check EnergiDataService  │
         │ SpotPriceType    │  │ hass.states.get(         │
         │ .GESpot          │  │   "sensor.energi_data_   │
         └──────────────────┘  │   service")              │
                               └──────────┬───────────────┘
                                          │
                               ┌──────────▼──────────┐
                               │ EDS found?          │
                               └──────────┬──────────┘
                                          │
                               ┌──────────▼────────┬──────┐
                               │ YES               │ NO   │
                               │                   │      │
                               ▼                   ▼
                     ┌──────────────────┐  ┌──────────────┐
                     │ Return           │  │ Return       │
                     │ SpotPriceType    │  │ SpotPriceType│
                     │ .EnergiDataServ  │  │ .NordPool    │
                     └──────────────────┘  │ (fallback)   │
                                           └──────────────┘

Priority:
1. Explicit user choice (highest)
2. GE-Spot (auto-detected) ◄── NEW!
3. EnergiDataService (auto-detected)
4. Nordpool (fallback - lowest)
```

## Component Relationships

```
┌────────────────────────────────────────────────────────────┐
│                      SpotPriceBase                         │
│  (Abstract Base Class)                                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Properties:                                          │ │
│  │ • is_initialized, currency, state, use_cent          │ │
│  │ • source, average_month, average_weekly, etc.        │ │
│  │                                                       │ │
│  │ Abstract Methods:                                     │ │
│  │ • async_set_dto(ret, initial)                        │ │
│  │ • setup()                                            │ │
│  │                                                       │ │
│  │ Concrete Methods:                                     │ │
│  │ • async_update_spotprice()                           │ │
│  │ • async_update_set_prices(dto)                       │ │
│  │ • async_update_average()                             │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────┬─────────────┬────────────┬─────────────────┘
               │             │            │
    ┌──────────▼──┐   ┌──────▼─────┐  ┌──▼──────────┐
    │ NordPool    │   │ EnergiData │  │  GESpot     │ ◄── NEW!
    │ Updater     │   │  Service   │  │  Updater    │
    │             │   │  Updater   │  │             │
    └──────┬──────┘   └──────┬─────┘  └──┬──────────┘
           │                 │            │
    ┌──────▼──────┐   ┌──────▼─────┐  ┌──▼──────────┐
    │ Nordpool    │   │ EnergiData │  │  GESpot     │ ◄── NEW!
    │    DTO      │   │    DTO     │  │    DTO      │
    └─────────────┘   └────────────┘  └─────────────┘
           │                 │            │
           └─────────────────┴────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   ISpotPriceDTO       │
              │   (Interface)         │
              │                       │
              │ • today: list         │
              │ • tomorrow: list      │
              │ • currency: str       │
              │ • average: float      │
              │ • tomorrow_valid:bool │
              └───────────────────────┘
```

---

**Note**: All diagrams use ASCII art for maximum compatibility and can be viewed in any text editor or markdown viewer.
