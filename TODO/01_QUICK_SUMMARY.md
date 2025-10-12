# GE-Spot Implementation - Quick Summary

## Overview
Add GE-Spot support to peaqevcore library (shared between peaqhvac and peaqev) following the code owner's architecture requirements.

## Key Points

### 1. What Goes Where

**peaqevcore (Core Library)**:
- ✅ GE-Spot detection logic
- ✅ GE-Spot data parsing (DTO)
- ✅ GE-Spot updater class
- ✅ Factory integration
- ✅ Constants and enums
- ✅ Tests

**peaqhvac (Integration)**:
- ✅ Updated manifest.json (add "ge_spot" dependency)
- ✅ Version bump for peaqevcore requirement
- ❌ NO custom GE-Spot code (it's in peaqevcore!)

### 2. Architecture Pattern

```
GE-Spot follows the EXACT same pattern as Nordpool:

SpotPriceFactory
    └─> Auto-detects available sources
        ├─> GESpotUpdater (NEW - like NordPoolUpdater)
        │   └─> GESpotDTO (NEW - like NordpoolDTO)
        ├─> NordPoolUpdater
        │   └─> NordpoolDTO
        └─> EnergiDataServiceUpdater
            └─> EnergiDataServiceDTO
```

### 3. Files to Create/Modify

#### peaqevcore Repository

**Create (3 files)**:
1. `peaqevcore/common/spotprice/gespot.py` (~150 lines)
2. `peaqevcore/tests/test_gespot.py` (~200 lines)
3. `peaqevcore/tests/test_spotprice_factory_gespot.py` (~100 lines)

**Modify (4 files)**:
1. `peaqevcore/common/spotprice/const.py` (+1 line)
2. `peaqevcore/common/spotprice/models/spotprice_dto.py` (+120 lines)
3. `peaqevcore/common/spotprice/models/spotprice_type.py` (+2 lines)
4. `peaqevcore/common/spotprice/spotprice_factory.py` (+25 lines)

#### peaqhvac Repository

**Modify (1 file)**:
1. `custom_components/peaqhvac/manifest.json` (+2 lines)

### 4. Key Technical Decisions

**GE-Spot Data Handling**:
- GE-Spot provides 96 intervals (15-minute data)
- We aggregate to 24 hourly values for compatibility
- Method: Average 4 consecutive 15-min intervals

**Auto-Detection Priority**:
1. Explicit user choice (if set)
2. GE-Spot (if found) ← NEW, high priority
3. EnergiDataService (if found)
4. Nordpool (fallback)

**Why GE-Spot has higher priority**:
- More universal (supports more regions)
- Modern integration with good reliability
- Users installing it likely want to use it

### 5. Testing Strategy

**Unit Tests**:
- DTO transformation (96→24 intervals)
- Error handling
- Attribute parsing

**Integration Tests**:
- Factory detection
- Multi-source scenarios
- Fallback behavior

**Manual Tests**:
- Fresh install with GE-Spot
- Migration from Nordpool
- Custom sensor override
- Data accuracy verification

### 6. Zero Breaking Changes

**For existing users**:
- If they don't have GE-Spot: Nothing changes
- If they install GE-Spot: Auto-detected and used
- If they have custom config: Honored

**Backward compatibility**: 100%
- All changes are additive
- No modifications to existing code paths
- Existing tests unchanged

### 7. Work Estimate

- **peaqevcore implementation**: 6-7 hours
- **peaqhvac update**: 1 hour
- **Testing**: 3-4 hours
- **Total**: ~11-13 hours

### 8. Quick Start Commands

```bash
# For peaqevcore development:
cd /workspaces/peaqev-core
# Create gespot.py, update factory, add tests
pytest tests/test_gespot.py
pytest tests/test_spotprice_factory_gespot.py

# For peaqhvac update:
cd /workspaces/hass-peaqhvac_temp
# Update manifest.json only
```

### 9. Success Criteria

- [x] Plan completed and reviewed
- [ ] peaqevcore changes implemented
- [ ] All tests pass (existing + new)
- [ ] peaqhvac manifest updated
- [ ] Manual testing completed
- [ ] Documentation updated
- [ ] PR created for peaqevcore
- [ ] Version released
- [ ] peaqhvac updated to use new version

### 10. Next Steps

1. **Review this plan** with code owner
2. **Create PR for peaqevcore** with implementation
3. **Wait for merge and release** of new peaqevcore version
4. **Update peaqhvac** to use new peaqevcore version
5. **Test end-to-end** with real GE-Spot integration

---

## Key Insight

The code owner wants **centralized pricing modules** in peaqevcore because:
- Both peaqhvac and peaqev need price data
- Avoid code duplication
- Single source of truth
- Easier maintenance
- Consistent behavior

**This is the right architectural decision!** ✅

---

See `IMPLEMENTATION_PLAN_GE_SPOT.md` for full detailed plan.
