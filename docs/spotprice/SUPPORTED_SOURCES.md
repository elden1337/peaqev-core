# Supported Electricity Price Sources

**Last Updated**: October 2025  
**peaqevcore Version**: 19.12.0+

---

## Quick Reference

| Source | Regions | Format | Priority | Status | Since |
|--------|---------|--------|----------|--------|-------|
| **GE-Spot** | Multi-region (EU, Nordic, Americas, Asia) | 96 × 15min | 1 (Highest) | ✅ Stable | v19.12.0 |
| **Energi Data Service** | Denmark | 24 × hourly | 2 | ✅ Stable | v19.x.x |
| **Nordpool** | Nordic (SE, NO, DK, FI) | 24 × hourly | 3 | ✅ Stable | Legacy |

---

## Detailed Comparison

### GE-Spot

**Integration**: https://github.com/enoch85/ge-spot  
**Home Assistant Domain**: `ge_spot`  
**Since**: peaqevcore v19.12.0

#### Coverage
- **Regions**: European Union, Nordic countries, North America, Asia-Pacific
- **Markets**: ENTSO-E, Nordpool, EIA, and more
- **Countries**: 50+ countries supported

#### Data Format
```python
{
    "state": "1.45",  # Current price
    "attributes": {
        "today": [...],     # 96 × 15-minute prices
        "tomorrow": [...],  # 96 × 15-minute prices (after ~13:00)
        "average": 1.38,    # Average price
        "unit": "SEK/kWh"
    }
}
```

#### Key Features
- ✅ 15-minute interval data (most granular)
- ✅ Multiple source fallbacks
- ✅ Timezone-aware
- ✅ Automatic unit detection
- ✅ Multi-region support

#### Use Cases
- **Best for**: Users outside Nordic countries
- **Best for**: Need for granular pricing data
- **Best for**: Regions with multiple available sources
- **Best for**: Backup/fallback requirements

#### Example Entities
- `sensor.ge_spot_sweden_se3`
- `sensor.ge_spot_germany_de`
- `sensor.ge_spot_france_fr`

#### Implementation Details
- **DTO**: `GESpotDTO` - Aggregates 96 intervals to 24 hourly
- **Updater**: `GESpotUpdater`
- **Tests**: 12 DTO tests, 3 factory tests
- **Documentation**: [GE_SPOT.md](GE_SPOT.md)

---

### Energi Data Service

**Integration**: Built into Home Assistant  
**Home Assistant Domain**: `energidataservice`  
**Since**: peaqevcore v19.x.x (exact version TBD)

#### Coverage
- **Regions**: Denmark only
- **Markets**: Danish Energy Agency (official source)
- **Areas**: DK1, DK2

#### Data Format
```python
{
    "state": "0.45",
    "attributes": {
        "today": [...],     # 24 × hourly prices
        "tomorrow": [...],  # 24 × hourly prices
        # ... various Danish-specific attributes
    }
}
```

#### Key Features
- ✅ Official Danish government source
- ✅ Hourly prices
- ✅ Most authoritative for Denmark
- ✅ Built into Home Assistant core

#### Use Cases
- **Best for**: Danish users
- **Best for**: Official/compliance requirements
- **Best for**: DK1/DK2 price areas

#### Example Entities
- `sensor.energi_data_service`

#### Implementation Details
- **DTO**: `EnergiDataServiceDTO`
- **Updater**: `EnergiDataServiceUpdater`
- **Priority**: Higher than Nordpool for Danish users

---

### Nordpool

**Integration**: https://github.com/custom-components/nordpool  
**Home Assistant Domain**: `nordpool`  
**Since**: peaqevcore legacy (earliest version)

#### Coverage
- **Regions**: Nordic countries
- **Markets**: Nord Pool electricity exchange
- **Countries**: Sweden, Norway, Denmark, Finland, Estonia, Latvia, Lithuania

#### Data Format
```python
{
    "state": "1.45",
    "attributes": {
        "today": [...],     # 24 × hourly prices
        "tomorrow": [...],  # 24 × hourly prices
        "average": 1.38,
        # ... Nordpool-specific attributes
    }
}
```

#### Key Features
- ✅ Well-established, stable
- ✅ Hourly prices
- ✅ Large user base
- ✅ Comprehensive Nordic coverage

#### Use Cases
- **Best for**: Nordic country users
- **Best for**: Users wanting established/proven solution
- **Best for**: PeaqEv system (legacy compatibility)

#### Example Entities
- `sensor.nordpool_kwh_se3_sek_3_10_025`
- `sensor.nordpool_kwh_oslo_nok_3_10_0`

#### Implementation Details
- **DTO**: `NordpoolDTO`
- **Updater**: `NordpoolUpdater`
- **Priority**: Fallback for most systems, preferred for PeaqEv
- **Special**: PeaqEv system always prefers Nordpool (legacy compatibility)

---

## Detection Priority

The `SpotPriceFactory` automatically detects price sources in this order:

```
1. GE-Spot
   ↓ Not found
2. Energi Data Service (Denmark)
   ↓ Not found
3. Nordpool (fallback)
```

**Exception**: PeaqEv system checks Nordpool first for legacy compatibility.

### Priority Rationale

**Why GE-Spot is highest priority:**
- Most regions supported
- Fallback mechanisms built-in
- Most granular data (15-min intervals)
- Continues to work if primary source fails

**Why Energi Data Service is second:**
- Official source for Denmark
- More authoritative than alternatives for DK

**Why Nordpool is fallback:**
- Well-established and stable
- Good coverage for Nordic countries
- Proven reliability

---

## Usage Examples

### Automatic Detection

```python
# Factory automatically selects best available source
from peaqevcore.common.spotprice.spotprice_factory import SpotPriceFactory

updater = await SpotPriceFactory.create(
    hub=hub,
    observer=observer,
    system=PeaqSystem.PeaqHvac
)

# Check which was selected
print(updater.source)  # "ge_spot", "energidataservice", or "nordpool"
```

### Force Specific Source

```python
from peaqevcore.common.spotprice.models.spotprice_type import SpotPriceType

# Force GE-Spot
updater = await SpotPriceFactory.create(
    hub=hub,
    observer=observer,
    system=PeaqSystem.PeaqEv,
    spotprice_type=SpotPriceType.GESpot
)

# Force Nordpool
updater = await SpotPriceFactory.create(
    hub=hub,
    observer=observer,
    system=PeaqSystem.PeaqHvac,
    spotprice_type=SpotPriceType.Nordpool
)
```

### Use Specific Entity

```python
# Specify exact sensor entity
updater = await SpotPriceFactory.create(
    hub=hub,
    observer=observer,
    system=PeaqSystem.PeaqHvac,
    custom_sensor="sensor.ge_spot_sweden_se3"
)
```

---

## Data Normalization

All sources are normalized to the same output format:

```python
SpotPriceModel(
    price_aware=True,              # Successfully loaded prices
    today=[0.10, 0.12, ...],       # 24 hourly prices (floats)
    tomorrow=[0.11, 0.13, ...],    # 24 hourly prices (may be empty)
    average=0.125,                 # Average of today's prices
    affected_date=datetime(...)    # Date the prices apply to
)
```

**Guaranteed**:
- `today` is always a list of 24 floats (or empty on failure)
- `tomorrow` is always a list of 24 floats (or empty if not available)
- `average` is always a float (0.0 if unavailable)
- `price_aware` is `True` only if prices successfully loaded

---

## Update Schedules

| Source | Update Time | Frequency | Tomorrow Available |
|--------|------------|-----------|-------------------|
| **GE-Spot** | Varies by region | 1-4 times/day | After ~13:00 CET (EU) |
| **Energi Data Service** | ~13:00 CET | Daily | After ~13:00 CET |
| **Nordpool** | ~13:00 CET | Daily | After ~13:00 CET |

**Note**: Times are approximate. Actual updates depend on the source integration.

---

## Regional Recommendations

### Sweden, Norway, Finland
- **Primary**: GE-Spot or Nordpool
- **Fallback**: The other one

### Denmark
- **Primary**: Energi Data Service (official)
- **Fallback**: GE-Spot or Nordpool

### Germany, France, Other EU
- **Primary**: GE-Spot (only option via peaqevcore)
- **Alternative**: Install other HA price integrations and add support (see [ADDING_NEW_SOURCE.md](ADDING_NEW_SOURCE.md))

### United States, Canada
- **Primary**: GE-Spot (EIA data)
- **Alternative**: Add support for local price integrations

### Other Regions
- **Primary**: GE-Spot (check supported regions)
- **Alternative**: Contribute support for local integrations

---

## Troubleshooting

### No Price Source Detected

**Symptom**: `price_aware = False`, no prices available

**Solution**:
1. Install a price integration in Home Assistant
2. Verify entity exists: `sensor.ge_spot_*` or `sensor.nordpool_*`
3. Check entity has `today` attribute with prices
4. Enable debug logging to see detection process

### Wrong Source Selected

**Symptom**: Factory chose source you don't want

**Solution**:
```python
# Force your preferred source
updater = await SpotPriceFactory.create(
    hub=hub,
    observer=observer,
    system=system,
    spotprice_type=SpotPriceType.Nordpool  # or GESpot, EnergidataService
)
```

### Prices in Wrong Unit

**Symptom**: Prices seem 100x too high or too low

**Cause**: DTO failed to detect cents vs currency

**Solution**:
- GE-Spot: Check `unit_of_measurement` attribute in sensor
- DTOs use heuristic: average > 50 = cents
- If persistent, report issue with your sensor data format

### Missing Tomorrow Prices

**Symptom**: `tomorrow` list is empty

**Expected**: Tomorrow's prices typically publish around 13:00 CET

**Not a bug if**:
- Time is before ~13:00 CET
- It's a weekend/holiday
- Source hasn't published yet

**Bug if**:
- Time is after 15:00 CET
- `today` has prices but `tomorrow` consistently empty
- Check source integration logs

---

## Performance Comparison

| Source | Memory | CPU (update) | Network | Latency |
|--------|--------|--------------|---------|---------|
| **GE-Spot** | ~2KB | <5ms | Zero¹ | <10ms |
| **Energi Data Service** | ~1KB | <3ms | Zero¹ | <5ms |
| **Nordpool** | ~1KB | <3ms | Zero¹ | <5ms |

¹All data comes from local Home Assistant entities; peaqevcore makes no external calls.

---

## Future Sources

Want to add support for a new price source? See [ADDING_NEW_SOURCE.md](ADDING_NEW_SOURCE.md).

**Potential Future Additions**:
- EPEX Spot (European Power Exchange)
- Tibber (if they open API)
- Octopus Energy
- Your region's price source

---

## Migration Guide

### From Custom Implementation

If you had custom GE-Spot code in your integration:

**Before** (hass-peaqhvac with custom factory):
```python
# Custom SpotPriceFactory in integration
from .spotprice.spotprice_factory import SpotPriceFactory

updater = await SpotPriceFactory.create(...)  # Custom implementation
```

**After** (peaqevcore v19.12.0+):
```python
# Use core implementation
from peaqevcore.common.spotprice.spotprice_factory import SpotPriceFactory

updater = await SpotPriceFactory.create(...)  # Auto-detects GE-Spot
```

**Changes Needed**:
1. Remove custom factory code
2. Update `manifest.json`: Add `"ge_spot"` to `after_dependencies`
3. Update `manifest.json`: Require `peaqevcore>=19.12.0`
4. Remove custom tests
5. Test that auto-detection works

See [hass-peaqhvac PR #151](https://github.com/elden1337/hass-peaqhvac/pull/151) as example.

---

## FAQ

**Q: Can I use multiple price sources simultaneously?**  
A: One source is used at a time, selected by factory priority. Multiple can be installed, but only one is active.

**Q: Which source is most accurate?**  
A: All sources are accurate. Choose based on region:
- Denmark: Energi Data Service (official)
- Nordic: Nordpool or GE-Spot
- Other EU: GE-Spot
- US/Canada: GE-Spot

**Q: Why does GE-Spot have higher priority than Nordpool?**  
A: GE-Spot has fallback mechanisms and wider coverage. If both are available, GE-Spot is more resilient.

**Q: Can I add my own price source?**  
A: Yes! See [ADDING_NEW_SOURCE.md](ADDING_NEW_SOURCE.md) for step-by-step guide.

**Q: What if my region isn't supported?**  
A: 
1. Check if GE-Spot supports it
2. Find a Home Assistant price integration for your region
3. Add support to peaqevcore (we welcome PRs!)

**Q: Does switching sources affect my optimization?**  
A: No. All sources output the same normalized format, so consumer integrations work identically.

---

## Related Documentation

- [Spot Price System Overview](README.md)
- [GE-Spot Integration Details](GE_SPOT.md)
- [Adding a New Price Source](ADDING_NEW_SOURCE.md)
- [Architecture Documentation](../ARCHITECTURE.md)

---

## External Links

- **GE-Spot**: https://github.com/enoch85/ge-spot
- **Nordpool Integration**: https://github.com/custom-components/nordpool
- **Energi Data Service**: Built into Home Assistant Core

---

**Need help?** Open an issue on [GitHub](https://github.com/elden1337/peaqev-core/issues) or ask in [Discussions](https://github.com/elden1337/peaqev-core/discussions).
