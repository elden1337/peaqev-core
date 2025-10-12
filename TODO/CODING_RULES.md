# Coding Rules (from GE-Spot Project)

**Source**: https://github.com/enoch85/ge-spot/.github/copilot-instructions.md

---

## Core Principles

• **Read entire files before editing** - Never edit based on grep/partial reads  
• **Configuration-driven, never hardcode** - All values from `const/` modules  
• **Generic naming only** - `interval_prices`, not `hourly_prices` or `15min_data`  
• **No backward compatibility** - Rename directly, update all callers, no aliases  
• **Test after every change** - Clear `__pycache__`, run tests, verify logs  
• **No verbose summaries** - User sees changes in editor, only respond if asked  
• **Keep it simple** - Clean code over complexity, cleanup as you go  
• **Ask before acting** - When uncertain, clarify first  
• **No analysis/summary files in git** - All `*ANALYSIS*.md`, `*SUMMARY*.md` stay untracked  

---

## Configuration-Driven

```python
# ✅ Correct
from ..const.spotprice import GESPOT
source = GESPOT

# ❌ Wrong
source = "ge_spot"  # NEVER hardcode
```

---

## Generic Naming

```python
# ✅ Generic
normalize_interval_prices()
interval_key
IntervalCalculator

# ❌ Specific
normalize_hourly_prices()
hour_key
QuarterHourCalculator
```

---

## No Backward Compatibility

```python
# ❌ Don't create aliases
def old_name(*args, **kwargs):
    return new_name(*args, **kwargs)

# ✅ Just rename and update ALL callers
def new_name(data, ...):
    # implementation
```

---

## Verify Your Work

```bash
# Search for old terms
grep -r "old_function_name" custom_components/

# Find hardcoded values
grep -r "= 96" custom_components/

# Test imports
python3 -c "from module import NewClass"
```

---

## Code Standards

• **Imports**: Group as stdlib, third-party, local. Relative imports within package  
• **Error Handling**: Specific exceptions, log with context, graceful fallback  
• **Type Hints**: Required on all functions. Use `Optional`, `Union`, `Dict[str, Any]`  
• **Async**: Almost everything is async. Use `await`  
• **Docstrings**: Every public function/class. Include types, example for complex functions  
• **Comments**: Explain WHY, not WHAT. Update or remove when changing code  

```python
# ✅ Error handling
try:
    result = api.fetch_data()
except APIError as e:
    _LOGGER.error(f"API fetch failed: {e}")
    return cached_data
```

---

## Testing

• **Priority**: Test production code, not test helpers  
• **Mock**: External APIs with rate limits/costs, slow operations  
• **Real Calls**: Integration tests, parser validation, smoke tests  

```python
# ✅ Test production
def test_api_fetch_real_data():
    api = ProductionAPI(api_key="test_key")
    result = api.fetch_data(region="TEST")
    assert result is not None
    assert len(result["data"]) > 0

# ❌ Test mocks
def test_mock_returns_structure():
    mock_data = create_mock_data()
    assert mock_data["field"] == "expected"
```

---

## Refactoring

**Phase Order**:
```
Foundation → Data → Logic → Presentation → Support
Constants → Structures → Processors → Sensors → Tests
Base classes → APIs → Coordinators → Config → Utils
```

**Before claiming phase complete**:
- [ ] All files updated (including base classes, validators, tests)
- [ ] All names changed (variables, functions, classes)
- [ ] All docs updated (docstrings, comments, type hints)
- [ ] All imports/callers updated
- [ ] Tests pass, no syntax errors
- [ ] Grep shows no old terms (except explanatory comments)
- [ ] No duplicates or dead code

**Commit after each phase**:
```bash
git commit -m "Phase N: Description
- Change 1
- Change 2
Tests: passing"
```

---

## Common Mistakes

❌ **Editing without full context** - Read entire file, not grep results  
❌ **Hardcoding values** - Use constants  
❌ **Incomplete refactoring** - Search ALL occurrences, update ALL (including tests)  
❌ **Mixed terminology** - Complete one layer at a time  
❌ **Forgetting base classes** - Update base classes first  
❌ **Outdated documentation** - Update docstrings, comments, type hints with code  

---

## Code Quality

**Remove dead code immediately**:
```python
# ❌ Don't leave
UNUSED_VAR = True  # Never used

# ✅ Delete it
```

**Fix duplicates**:
```python
# ❌ Same file
MAX = 100  # Line 18
MAX = 10   # Line 26 (overwrites!)

# ✅ One definition
MAX = 1000  # Single value
```

**Document calculations**:
```python
# ✅ Show math
# 3 days × 24 hours × 4 intervals/hour × 10 areas × 1.2 buffer
# = 3,456 → round to 3,500
CACHE_MAX = 3500
```

**Prefer content checks over time-based**:
```python
# ❌ Time-based
if time.time() - cached_time < MAX_AGE:
    return cached_data

# ✅ Content-based
if cached_data.get("statistics", {}).get("data_complete"):
    return cached_data
```

---

## Summary

**Quality and correctness over speed. When uncertain, ask before implementing.**
