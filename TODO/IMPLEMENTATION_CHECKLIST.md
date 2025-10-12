# GE-Spot Implementation Checklist

**Project**: Add GE-Spot support to peaqevcore  
**Date Started**: ___________  
**Developer**: ___________  
**Target Completion**: ___________

---

## Pre-Implementation

- [ ] Review full implementation plan (`IMPLEMENTATION_PLAN_GE_SPOT.md`)
- [ ] Review architecture diagrams (`ARCHITECTURE_DIAGRAMS.md`)
- [ ] Set up development environment
- [ ] Clone/fork peaqevcore repository
- [ ] Create feature branch in peaqevcore: `git checkout -b feature/gespot-support`
- [ ] Verify peaqevcore tests run: `pytest`
- [ ] Review GE-Spot integration documentation

---

## Phase 1: peaqevcore Core Implementation

### Step 1.1: Constants Update
**File**: `peaqevcore/common/spotprice/const.py`

- [ ] Add `GESPOT = "ge_spot"` constant
- [ ] Verify imports in other files if needed
- [ ] Run tests to ensure no breakage

**Code**:
```python
NORDPOOL = "nordpool"
ENERGIDATASERVICE = "energidataservice"
GESPOT = "ge_spot"  # ADD THIS LINE
ENERGIDATASERVICE_SENSOR = "sensor.energi_data_service"
AVERAGE_MAX_LEN = 31
```

---

### Step 1.2: SpotPriceType Enum Update
**File**: `peaqevcore/common/spotprice/models/spotprice_type.py`

- [ ] Import GESPOT constant
- [ ] Add `GESpot = GESPOT` to enum
- [ ] Verify enum works correctly

**Code**:
```python
from enum import Enum
from peaqevcore.common.spotprice.const import NORDPOOL, ENERGIDATASERVICE, GESPOT

class SpotPriceType(Enum):
    NordPool = NORDPOOL
    EnergidataService = ENERGIDATASERVICE
    GESpot = GESPOT  # ADD THIS LINE
```

---

### Step 1.3: GESpotDTO Creation
**File**: `peaqevcore/common/spotprice/models/spotprice_dto.py`

- [ ] Create `GESpotDTO` class
- [ ] Implement `_set_price_in_cent()` method
- [ ] Implement `_set_average()` method
- [ ] Implement `_set_affected_date()` method
- [ ] Implement `_aggregate_to_hourly()` helper method
- [ ] Override `set_model()` method
- [ ] Add comprehensive docstrings
- [ ] Test aggregation logic manually

**Key Code Sections**:
```python
@dataclass
class GESpotDTO(ISpotPriceDTO):
    """Data Transfer Object for GE-Spot integration."""
    
    def _aggregate_to_hourly(self, interval_data: list) -> list:
        """Aggregate 15-minute intervals to hourly data."""
        # Implementation here...
    
    # Other methods...
```

**Testing checkpoint**:
```python
# Quick manual test
dto = GESpotDTO()
test_96 = [float(i) for i in range(96)]
result = dto._aggregate_to_hourly(test_96)
assert len(result) == 24
assert result[0] == 1.5  # (0+1+2+3)/4
```

---

### Step 1.4: GESpotUpdater Creation
**File**: `peaqevcore/common/spotprice/gespot.py` (NEW FILE)

- [ ] Create new file `gespot.py`
- [ ] Import required dependencies
- [ ] Create `GESpotUpdater` class extending `SpotPriceBase`
- [ ] Implement `__init__()` method
- [ ] Implement `async_set_dto()` method
- [ ] Implement `setup()` method
- [ ] Implement `_setup_set_entity()` helper method
- [ ] Add comprehensive docstrings
- [ ] Add logging statements

**Verification**:
```bash
# Check syntax
python -m py_compile peaqevcore/common/spotprice/gespot.py

# Check imports work
python -c "from peaqevcore.common.spotprice.gespot import GESpotUpdater; print('OK')"
```

---

### Step 1.5: SpotPriceFactory Update
**File**: `peaqevcore/common/spotprice/spotprice_factory.py`

- [ ] Import `GESpotUpdater`
- [ ] Add `GESpot: GESpotUpdater` to `sources` dict
- [ ] Update `test_connections()` method with GE-Spot detection
- [ ] Add GE-Spot priority logic
- [ ] Add logging for detection
- [ ] Test import doesn't break existing code

**Code Changes**:
```python
from peaqevcore.common.spotprice.gespot import GESpotUpdater  # ADD

class SpotPriceFactory:
    sources = {
        SpotPriceType.NordPool: NordPoolUpdater,
        SpotPriceType.EnergidataService: EnergiDataServiceUpdater,
        SpotPriceType.GESpot: GESpotUpdater  # ADD
    }
    
    @staticmethod
    def test_connections(hass, spotprice_type, system, custom_sensor=None):
        # Add GE-Spot detection logic
        # ...
```

**Verification**:
```bash
# Test factory still works
pytest peaqevcore/tests/test_spotprice_factory.py -v
```

---

## Phase 2: Testing Implementation

### Step 2.1: Unit Tests for GESpotDTO
**File**: `peaqevcore/tests/test_gespot.py` (NEW FILE)

- [ ] Create test file
- [ ] Create fixtures (mock_hub, mock_observer, sample_state)
- [ ] Test `_aggregate_to_hourly()` with 96 intervals
- [ ] Test `_aggregate_to_hourly()` with 24 intervals
- [ ] Test `_aggregate_to_hourly()` with None values
- [ ] Test `set_model()` with full state
- [ ] Test `_set_average()` with various inputs
- [ ] Test `_set_price_in_cent()` detection
- [ ] Test `_set_affected_date()` parsing
- [ ] Run tests: `pytest peaqevcore/tests/test_gespot.py -v`

**Coverage Check**:
```bash
pytest peaqevcore/tests/test_gespot.py --cov=peaqevcore.common.spotprice.gespot --cov-report=term-missing
# Target: >90% coverage
```

---

### Step 2.2: Unit Tests for GESpotUpdater
**File**: `peaqevcore/tests/test_gespot.py` (continue)

- [ ] Test `__init__()` initialization
- [ ] Test `async_set_dto()` with initial=True
- [ ] Test `async_set_dto()` with initial=False
- [ ] Test `setup()` with single entity
- [ ] Test `setup()` with multiple entities
- [ ] Test `setup()` with no entities
- [ ] Test `setup()` with custom sensor
- [ ] Run all tests: `pytest peaqevcore/tests/test_gespot.py -v`

---

### Step 2.3: Integration Tests for Factory
**File**: `peaqevcore/tests/test_spotprice_factory_gespot.py` (NEW FILE)

- [ ] Create test file
- [ ] Test `test_connections()` detects GE-Spot
- [ ] Test `test_connections()` prioritizes correctly
- [ ] Test `test_connections()` falls back when GE-Spot absent
- [ ] Test `create()` returns GESpotUpdater when appropriate
- [ ] Test `create()` with custom sensor
- [ ] Run tests: `pytest peaqevcore/tests/test_spotprice_factory_gespot.py -v`

---

### Step 2.4: Regression Tests
- [ ] Run ALL existing tests: `pytest peaqevcore/tests/ -v`
- [ ] Verify no test failures
- [ ] Verify no test warnings
- [ ] Check test coverage: `pytest --cov=peaqevcore`
- [ ] Target: No decrease in overall coverage

**Command**:
```bash
# Run full test suite
pytest peaqevcore/tests/ -v --cov=peaqevcore --cov-report=html

# Check for regressions
git diff main --stat  # Review changes
```

---

## Phase 3: Code Quality & Documentation

### Step 3.1: Code Quality Checks
- [ ] Run linter: `flake8 peaqevcore/common/spotprice/gespot.py`
- [ ] Run type checker: `mypy peaqevcore/common/spotprice/gespot.py`
- [ ] Check docstring coverage
- [ ] Verify logging levels appropriate
- [ ] Check for code duplication
- [ ] Review error handling completeness

**Tools**:
```bash
# Linting
flake8 peaqevcore/common/spotprice/ --max-line-length=120

# Type checking (if mypy configured)
mypy peaqevcore/common/spotprice/gespot.py

# Complexity check
radon cc peaqevcore/common/spotprice/gespot.py -a
```

---

### Step 3.2: Documentation Updates
- [ ] Update `README.md` with GE-Spot support mention
- [ ] Update `CHANGELOG.md` with changes
- [ ] Add/update API documentation
- [ ] Add code examples if applicable
- [ ] Update version number in `setup.py` or `pyproject.toml`

**Version Update**:
```python
# In setup.py or pyproject.toml
version = "19.11.3"  # Increment from 19.11.2
```

---

## Phase 4: Manual Testing

### Step 4.1: Environment Setup
- [ ] Set up Home Assistant test instance
- [ ] Install GE-Spot integration (v1.4.1+)
- [ ] Configure GE-Spot for test region (e.g., SE4)
- [ ] Verify GE-Spot sensor exists and has data
- [ ] Install peaqevcore development version
- [ ] Install peaqhvac for integration testing

---

### Step 4.2: Test Scenarios

**Test Case 1: Fresh Install**
- [ ] Fresh HA instance with only GE-Spot
- [ ] Install peaqhvac
- [ ] Verify GE-Spot auto-detected
- [ ] Check logs for correct initialization
- [ ] Verify price data flows correctly

**Test Case 2: Multi-Source Environment**
- [ ] HA instance with Nordpool AND GE-Spot
- [ ] Verify GE-Spot takes priority
- [ ] Check logs show correct source selection
- [ ] Verify data accuracy

**Test Case 3: Custom Sensor**
- [ ] Configure custom GE-Spot sensor
- [ ] Verify override works
- [ ] Check correct sensor used

**Test Case 4: Data Validation**
- [ ] Compare GE-Spot raw data (96 intervals)
- [ ] Compare peaqhvac processed data (24 hours)
- [ ] Verify aggregation is correct
- [ ] Check currency, average, tomorrow_valid

**Test Case 5: Fallback**
- [ ] Disable GE-Spot
- [ ] Verify fallback to Nordpool
- [ ] Re-enable GE-Spot
- [ ] Verify switch back to GE-Spot

---

### Step 4.3: Manual Test Log

| Test # | Description | Expected | Actual | Pass/Fail | Notes |
|--------|-------------|----------|--------|-----------|-------|
| 1      | Auto-detect GE-Spot | Detected | | | |
| 2      | Parse 96 intervals | 24 hours | | | |
| 3      | Correct averages | Match HA | | | |
| 4      | Tomorrow prices | When valid | | | |
| 5      | Currency correct | Match GE-Spot | | | |
| 6      | Fallback works | To Nordpool | | | |
| 7      | Custom sensor | Used correctly | | | |

---

## Phase 5: peaqhvac Integration

### Step 5.1: Manifest Update
**File**: `custom_components/peaqhvac/manifest.json`

- [ ] Add `"ge_spot"` to `after_dependencies`
- [ ] Update `peaqevcore` version to new release (e.g., `19.11.3`)
- [ ] Update peaqhvac version (e.g., `3.1.10`)
- [ ] Verify JSON syntax

**Changes**:
```json
{
  "after_dependencies": [
    "myuplink",
    "nordpool",
    "energidataservice",
    "ge_spot",  // ADD THIS
    "peaqev",
    "met"
  ],
  "requirements": [
    "peaqevcore==19.11.3"  // UPDATE THIS
  ],
  "version": "3.1.10"  // UPDATE THIS
}
```

---

### Step 5.2: Verification
- [ ] Verify no code changes needed in peaqhvac
- [ ] Check hub uses `SpotPriceFactory.create()`
- [ ] Test peaqhvac with new peaqevcore version
- [ ] Verify integration still works

---

## Phase 6: Release Process

### Step 6.1: peaqevcore Release
- [ ] Commit all changes: `git commit -m "feat: add GE-Spot support"`
- [ ] Push to feature branch: `git push origin feature/gespot-support`
- [ ] Create Pull Request to main
- [ ] Request code review
- [ ] Address review comments
- [ ] Merge to main
- [ ] Tag release: `git tag v19.11.3`
- [ ] Push tag: `git push --tags`
- [ ] Create GitHub release with notes
- [ ] Publish to PyPI (if applicable)

**PR Description Template**:
```markdown
## Add GE-Spot Support

Adds support for GE-Spot (Global Electricity Spot Prices) integration as a price source.

### Changes
- Added `GESpotUpdater` class following Nordpool pattern
- Added `GESpotDTO` for data transformation
- Updated `SpotPriceFactory` with GE-Spot auto-detection
- GE-Spot prioritized over EnergiDataService
- Handles 15-minute intervals (aggregates to hourly)

### Testing
- Comprehensive unit tests (>90% coverage)
- Integration tests for factory
- Manual testing with GE-Spot v1.4.1

### Backward Compatibility
- ✅ All existing tests pass
- ✅ No breaking changes
- ✅ Auto-detection maintains fallback logic

Closes #XXX (if issue exists)
```

---

### Step 6.2: peaqhvac Release
- [ ] Update to new peaqevcore version
- [ ] Test thoroughly
- [ ] Commit changes: `git commit -m "feat: add GE-Spot support via peaqevcore 19.11.3"`
- [ ] Create Pull Request
- [ ] Merge to main
- [ ] Tag release
- [ ] Create GitHub release

---

## Phase 7: Documentation & Communication

### Step 7.1: User Documentation
- [ ] Update peaqhvac README with GE-Spot info
- [ ] Add GE-Spot to supported price sources list
- [ ] Create configuration examples
- [ ] Update troubleshooting guide
- [ ] Add FAQ entries if needed

---

### Step 7.2: Release Notes
- [ ] Write comprehensive release notes
- [ ] Highlight GE-Spot support as new feature
- [ ] Document any configuration changes
- [ ] Mention automatic detection
- [ ] Link to GE-Spot integration

**Release Notes Template**:
```markdown
## peaqhvac v3.1.10

### New Features
- ✨ **GE-Spot Support**: Added support for GE-Spot (Global Electricity Spot Prices) integration
  - Automatic detection when GE-Spot is installed
  - Supports 15-minute interval data with smart aggregation
  - Higher priority than EnergiDataService
  - Zero configuration needed!

### Changes
- Updated peaqevcore to v19.11.3
- Added GE-Spot to after_dependencies

### Supported Price Sources
1. GE-Spot (global coverage)
2. Nordpool (Nordic/Baltic)
3. EnergiDataService (Denmark)

### Migration Notes
- No action needed for existing users
- To use GE-Spot: Just install it, peaqhvac will detect it automatically
```

---

### Step 7.3: Community Communication
- [ ] Announce on Home Assistant Community forum
- [ ] Update HACS repository metadata
- [ ] Respond to any questions/feedback
- [ ] Monitor for issues

---

## Post-Release

### Monitoring
- [ ] Monitor GitHub issues for GE-Spot-related problems
- [ ] Check logs in community reports
- [ ] Gather user feedback
- [ ] Track adoption metrics (if available)

### Future Improvements
- [ ] Consider keeping 15-minute granularity (breaking change)
- [ ] Add configuration option for interval preference
- [ ] Enhance multi-source fallback logic
- [ ] Add support for more price sources

---

## Rollback Plan (If Needed)

### If Issues Found in peaqevcore
1. [ ] Revert git tag
2. [ ] Publish hotfix version
3. [ ] Update peaqhvac to use previous version
4. [ ] Communicate issue to users

### If Issues Found in peaqhvac
1. [ ] Revert manifest changes
2. [ ] Use previous peaqevcore version
3. [ ] Create hotfix release
4. [ ] Document known issues

---

## Sign-off

**Developer**: _________________ Date: _________

**Code Reviewer**: _________________ Date: _________

**Tester**: _________________ Date: _________

**Release Manager**: _________________ Date: _________

---

## Notes & Issues Encountered

```
(Use this space to document any issues, workarounds, or important decisions made during implementation)







```

---

**Completion Date**: _________

**Status**: ☐ In Progress  ☐ Completed  ☐ On Hold  ☐ Cancelled
