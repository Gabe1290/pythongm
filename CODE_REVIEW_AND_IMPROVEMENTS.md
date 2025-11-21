# PyGameMaker 2 (pygm2) - Comprehensive Code Review & Improvement Plan

**Review Date:** November 21, 2025
**Reviewer:** Claude Code (Sonnet 4.5)
**Codebase Size:** ~3,408 Python files
**LOC (Key Files):** ~15,000+ lines in critical modules

---

## Executive Summary

PyGameMaker 2 is a well-architected GameMaker-style game engine and IDE built on PySide6 (Qt) and Pygame. The project demonstrates strong architectural design with signal-based communication, clear separation of concerns between IDE and runtime, and comprehensive GameMaker 8.0 event/action system implementation.

**Overall Assessment: GOOD foundation with significant technical debt**

### Strengths ✅
- Clean signal-based architecture (Qt signals for loose coupling)
- Comprehensive GM8.0 event/action system (9 event categories, 13 action tabs)
- Auto-discovery pattern for action handlers (excellent extensibility)
- Proper path handling (relative/absolute conversions)
- Graceful degradation (audio initialization handles headless systems)
- Well-structured project format (JSON-based with ZIP support)

### Critical Issues ❌
- **Massive monolithic files** (ide_window.py: 2,700+ lines)
- **Severe code duplication** in export modules (14 versions of kivy_exporter.py!)
- **Missing test infrastructure** (no pytest setup, ad-hoc test files)
- **Debugging code in production** (print statements everywhere)
- **Inconsistent error handling** (silent failures, missing validation)

---

## 1. Architecture Analysis

### 1.1 Layered Architecture ✅

```
┌─────────────────────────────────────────────┐
│  IDE Layer (PyGameMakerIDE)                 │
│  - Main window, menus, toolbars             │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  Managers Layer                             │
│  - ProjectManager (project lifecycle)       │
│  - AssetManager (asset operations)          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  Editors Layer                              │
│  - ObjectEditor (events/actions)            │
│  - RoomEditor (visual design)               │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  Runtime Layer                              │
│  - GameRunner (game loop, rendering)        │
│  - ActionExecutor (action execution)        │
│  - GameEngine (sprite loading, state)       │
└─────────────────────────────────────────────┘
```

**Assessment:** Well-designed separation of concerns.

### 1.2 Signal-Based Communication ✅

**Pattern Used:** Qt Signal/Slot system for loose coupling

**Examples:**
```python
# ProjectManager signals
project_loaded = Signal(Path, dict)
project_saved = Signal()
dirty_changed = Signal(bool)

# AssetManager signals
asset_imported = Signal(str, str, dict)
asset_updated = Signal(str, str, dict)
```

**Benefits:**
- Decoupled components
- Easy to extend
- Natural pub/sub pattern

**Concern:** No explicit signal disconnection strategy could lead to memory leaks in long-running sessions.

---

## 2. Critical Issues Analysis

### 2.1 Monolithic File Sizes 🔴 CRITICAL

**Problem:** Single Responsibility Principle severely violated

| File | Lines | Should Be |
|------|-------|-----------|
| `core/ide_window.py` | 2,700+ | ~10 separate modules |
| `editors/object_editor/object_editor_main.py` | 1,500+ | ~5 modules |
| `runtime/game_runner.py` | 1,100+ | ~4 modules |
| `runtime/game_engine.py` | 1,200+ | ~4 modules |
| `core/project_manager.py` | 900+ | ~3 modules |

**Impact:**
- Difficult to test individual components
- High cognitive load when reading
- Merge conflicts in team environment
- Slow IDE autocomplete/analysis

**Recommendation:** Refactor into smaller, focused modules (see Section 4).

---

### 2.2 Export Module Chaos 🔴 CRITICAL

**Problem:** Severe code duplication and unclear versioning

**Files Found:**
```
export/kivy_exporter.py
export/kivy_exporter.py.bak
export/kivy_exporter.py.bak2
export/kivy_exporter.py.bak3
export/kivy_exporter.py.bak4
export/kivy_exporter.py.rollback
export/kivy_exporter (conflicted copy).py
... (14 total versions!)
```

**Impact:**
- Unclear which version is "correct"
- Wasted disk space
- Confusion for developers
- Difficult to track changes

**Immediate Actions:**
1. **Identify the canonical version** (check git history + last modified dates)
2. **Delete all backup files** (use git branches for versioning!)
3. **Create export architecture documentation**
4. **Establish git workflow** to prevent future duplication

---

### 2.3 Missing Test Infrastructure 🔴 CRITICAL

**Current State:**
- Ad-hoc test files: `test_create_event.py`, `test_grid_movement.py`, etc.
- No pytest configuration
- No test organization (fixtures, mocks, parametrization)
- No CI/CD integration

**Impact:**
- Difficult to verify bug fixes
- No regression testing
- Fear of refactoring (will it break something?)
- Cannot safely modify core components

**Required:**
```
tests/
├── conftest.py              # Pytest fixtures
├── unit/
│   ├── test_project_manager.py
│   ├── test_asset_manager.py
│   └── test_action_executor.py
├── integration/
│   ├── test_project_workflow.py
│   └── test_game_execution.py
└── fixtures/
    ├── sample_project/
    └── test_assets/
```

---

### 2.4 Debugging Code in Production 🟡 MEDIUM

**Problem:** Excessive print statements throughout codebase

**Examples from reviewed files:**
```python
# project_manager.py
print(f"💾 DEBUG: save_project called with path: {project_path}")
print(f"💾 DEBUG: Saving to {project_file}")
print(f"💾 AssetManager: Saving room order: {room_order}")

# game_runner.py
print(f"\n⌨️  Key pressed: {sub_key}")
print(f"  📋 obj_player events: {list(events.keys())}")
print(f"✅ Movement allowed: {instance.object_name} → ({instance.intended_x}, {instance.intended_y})")
```

**Impact:**
- Cluttered output (hard to find actual errors)
- Performance overhead
- Unprofessional user experience

**Solution:**
```python
import logging
logger = logging.getLogger(__name__)

# Instead of print()
logger.debug("save_project called with path: %s", project_path)
logger.info("Project saved successfully")
logger.warning("Asset missing sprite reference")
logger.error("Failed to save project: %s", error)
```

**Benefits:**
- Configurable verbosity (DEBUG/INFO/WARNING/ERROR)
- Log to file for debugging
- Clean user-facing output
- Standard Python practice

---

## 3. Code Quality Issues

### 3.1 Inconsistent Error Handling 🟡 MEDIUM

**Pattern 1: Silent Failures**
```python
# asset_manager.py:89-94
try:
    self.asset_manager.asset_imported.disconnect(self.on_asset_changed)
except (RuntimeError, TypeError):
    pass  # ❌ Silently ignores disconnection errors
```

**Pattern 2: Bare Except Blocks**
```python
# game_runner.py:137
except:  # ❌ Catches ALL exceptions, even KeyboardInterrupt!
    return (135, 206, 235)  # Default sky blue
```

**Pattern 3: Exception Without Context**
```python
# action_executor.py:100
except Exception as e:
    print(f"❌ Error executing action {action_name}: {e}")
    import traceback
    traceback.print_exc()  # ❌ Traceback in production!
```

**Recommendation:**
```python
# ✅ BETTER: Specific exceptions with logging
try:
    self.asset_manager.asset_imported.disconnect(self.on_asset_changed)
except RuntimeError as e:
    logger.warning("Signal already disconnected: %s", e)
except TypeError as e:
    logger.error("Invalid signal connection: %s", e)
    raise  # Re-raise if unexpected

# ✅ BETTER: Specific exception handling
try:
    r = int(color_str[0:2], 16)
    g = int(color_str[2:4], 16)
    b = int(color_str[4:6], 16)
    return (r, g, b)
except (ValueError, IndexError) as e:
    logger.warning("Invalid color format '%s': %s. Using default.", color_str, e)
    return (135, 206, 235)
```

---

### 3.2 Mixed Path Handling 🟡 MEDIUM

**Issue:** Inconsistent use of `str` vs `Path` objects

**Current State:**
- `ProjectManager` uses `Path` objects ✅
- `AssetManager` converts to `str` internally ❌
- `GameRunner` uses `str` paths ❌

**Impact:**
- Confusing API (is this parameter a string or Path?)
- Error-prone (string concatenation vs `/` operator)
- Difficult to refactor

**Recommendation:**
```python
# ✅ CONSISTENT: Always use Path objects
from pathlib import Path

def load_project(self, project_path: Path) -> bool:
    """Load project from path"""
    project_path = Path(project_path)  # Convert if needed
    project_file = project_path / "project.json"  # Path operator
    # ... rest of implementation
```

---

### 3.3 Missing Type Hints 🟡 MEDIUM

**Current State:** Partial type hints, inconsistent usage

**Example from project_manager.py:**
```python
# ✅ HAS type hints
def create_new_project(self, project_name: str, location: Path) -> bool:
    ...

# ❌ MISSING type hints
def _validate_project_data(self, project_data):  # What type is project_data?
    ...
```

**Impact:**
- IDE autocomplete less effective
- Harder to catch type errors
- Unclear API contracts

**Recommendation:**
```python
# ✅ FULL type hints
from typing import Dict, Any, Optional

def _validate_project_data(self, project_data: Dict[str, Any]) -> bool:
    """Validate project data structure

    Args:
        project_data: Project configuration dictionary

    Returns:
        True if valid, False otherwise
    """
    required_keys = ["name", "version", "assets"]
    return all(key in project_data for key in required_keys)
```

---

### 3.4 Docstring Coverage 🟢 LOW PRIORITY

**Current State:** Minimal docstrings in critical modules

**Example:**
```python
# ❌ NO docstring
def _save_to_zip(self) -> bool:
    try:
        if not self._original_zip_path:
            print("No original zip path")
            return False
        # ... 20 lines of complex zip logic
```

**Recommendation:**
```python
# ✅ COMPREHENSIVE docstring
def _save_to_zip(self) -> bool:
    """Save project directly to original ZIP file

    This method:
    1. Saves to temporary extraction directory first
    2. Compresses temp directory to ZIP
    3. Creates backup before overwriting
    4. Restores backup on failure

    Returns:
        True if save successful, False otherwise

    Raises:
        FileNotFoundError: If original_zip_path doesn't exist
    """
```

---

## 4. Refactoring Recommendations

### 4.1 Split `ide_window.py` (2,700 lines → ~10 modules) 🔴 HIGH PRIORITY

**Proposed Structure:**
```
core/
├── ide_window.py          # 300 lines - Main window coordinator
├── menu_manager.py        # 200 lines - Menu bar creation
├── toolbar_manager.py     # 200 lines - Toolbar creation
├── tab_manager.py         # 200 lines - Editor tab management
├── status_manager.py      # 100 lines - Status bar updates
├── project_actions.py     # 300 lines - New/Open/Save/Close
├── asset_actions.py       # 300 lines - Import/Export/Delete
├── game_actions.py        # 200 lines - Play/Pause/Stop
└── export_manager.py      # 300 lines - Export coordination
```

**Benefits:**
- Each module has single responsibility
- Easier to test
- Clearer code organization
- Better IDE performance

---

### 4.2 Extract Action Execution Logic 🟡 MEDIUM PRIORITY

**Current:** `ActionExecutor` class with 40+ methods (action_executor.py:672 lines)

**Proposed:** Plugin-based architecture

```python
# actions/base.py
class ActionHandler(ABC):
    @abstractmethod
    def execute(self, instance, parameters: Dict[str, Any]) -> None:
        """Execute this action"""
        pass

# actions/movement.py
class MoveGridAction(ActionHandler):
    def execute(self, instance, parameters):
        direction = parameters.get("direction", "right")
        grid_size = int(parameters.get("grid_size", 32))
        # ... movement logic

# actions/score.py
class SetScoreAction(ActionHandler):
    def execute(self, instance, parameters):
        # ... score logic

# runtime/action_executor.py
class ActionExecutor:
    def __init__(self):
        self.handlers: Dict[str, ActionHandler] = {}
        self._discover_handlers()

    def _discover_handlers(self):
        """Auto-discover action handlers from actions/ directory"""
        # Use importlib to find all ActionHandler subclasses
```

**Benefits:**
- Each action in separate file
- Easier to test individual actions
- Plugin architecture for user extensions
- Cleaner separation of concerns

---

### 4.3 Introduce Repository Pattern for Asset Management 🟡 MEDIUM PRIORITY

**Current:** `AssetManager` handles both business logic AND file I/O

**Proposed:**
```python
# core/asset_repository.py
class AssetRepository:
    """Handles file I/O for assets (storage layer)"""

    def save_asset(self, asset_data: Dict, file_path: Path) -> bool:
        """Save asset to disk"""

    def load_asset(self, file_path: Path) -> Optional[Dict]:
        """Load asset from disk"""

    def delete_asset(self, file_path: Path) -> bool:
        """Delete asset file"""

# core/asset_manager.py
class AssetManager:
    """Handles asset business logic"""

    def __init__(self, repository: AssetRepository):
        self.repository = repository

    def import_asset(self, file_path: Path, asset_type: str) -> Optional[Dict]:
        """Business logic for importing"""
        # Validation
        if not self.is_supported_format(file_path, asset_type):
            return None
        # Delegate to repository
        return self.repository.save_asset(asset_data, dest_path)
```

**Benefits:**
- Easier to test (mock repository)
- Clearer separation (business logic vs I/O)
- Easier to swap storage backends (database, cloud, etc.)

---

## 5. Performance Optimizations

### 5.1 Asset Caching Strategy 🟢 LOW PRIORITY

**Current:** Unlimited cache in `AssetManager.assets_cache`

**Issue:** Large projects could consume significant memory

**Recommendation:**
```python
from functools import lru_cache
from collections import OrderedDict

class LRUAssetCache:
    """LRU cache with configurable size limit"""

    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                self.cache.popitem(last=False)
        self.cache[key] = value
```

---

### 5.2 Lazy Loading for Sprites 🟢 LOW PRIORITY

**Current:** All sprites loaded on project open

**Issue:** Slow startup for large projects

**Recommendation:**
```python
class LazySprite:
    """Sprite that loads on first access"""

    def __init__(self, sprite_path: Path):
        self.path = sprite_path
        self._surface = None

    @property
    def surface(self):
        if self._surface is None:
            self._surface = pygame.image.load(self.path)
        return self._surface
```

---

## 6. Testing Strategy

### 6.1 Unit Test Coverage Plan 🔴 HIGH PRIORITY

**Priority 1: Core Managers (Week 1)**
```
tests/unit/
├── test_project_manager.py
│   ├── test_create_project()
│   ├── test_load_project()
│   ├── test_save_project()
│   ├── test_project_validation()
│   └── test_dirty_flag_management()
│
└── test_asset_manager.py
    ├── test_import_asset()
    ├── test_rename_asset()
    ├── test_delete_asset()
    └── test_path_resolution()
```

**Priority 2: Action System (Week 2)**
```
tests/unit/
└── test_action_executor.py
    ├── test_action_discovery()
    ├── test_move_grid_action()
    ├── test_set_score_action()
    └── test_invalid_action_handling()
```

**Priority 3: Game Runtime (Week 3)**
```
tests/integration/
└── test_game_execution.py
    ├── test_room_loading()
    ├── test_create_event_execution()
    ├── test_collision_detection()
    └── test_keyboard_input()
```

---

### 6.2 Test Fixtures

**Required Fixtures:**
```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir

@pytest.fixture
def sample_project_data():
    """Minimal valid project data"""
    return {
        "name": "TestProject",
        "version": "1.0.0",
        "assets": {
            "sprites": {},
            "objects": {},
            "rooms": {
                "room0": {
                    "name": "room0",
                    "width": 1024,
                    "height": 768,
                    "instances": []
                }
            }
        }
    }

@pytest.fixture
def project_manager(temp_project_dir):
    """Create ProjectManager instance"""
    from core.project_manager import ProjectManager
    from core.asset_manager import AssetManager

    asset_mgr = AssetManager(temp_project_dir)
    pm = ProjectManager(asset_mgr)
    return pm
```

---

## 7. Priority Action Items

### Week 1: Critical Foundations 🔴

**1. Set Up Testing Infrastructure** (Day 1-2)
- [ ] Install pytest: `pip install pytest pytest-qt pytest-cov`
- [ ] Create `tests/conftest.py` with fixtures
- [ ] Write 10 unit tests for `ProjectManager`
- [ ] Set up CI/CD (GitHub Actions) to run tests

**2. Clean Up Export Modules** (Day 3)
- [ ] Audit all `kivy_exporter*.py` files
- [ ] Identify canonical version
- [ ] Delete backup files (.bak, .bak2, etc.)
- [ ] Document export architecture

**3. Replace Print Debugging** (Day 4-5)
- [ ] Add logging configuration to `main.py`
- [ ] Replace all `print()` in core modules with `logger.*`
- [ ] Create user-facing status updates (emit signals instead of print)

---

### Week 2: Code Quality 🟡

**4. Improve Error Handling** (Day 1-3)
- [ ] Replace bare `except:` with specific exceptions
- [ ] Add validation to all public API methods
- [ ] Create custom exception classes (`ProjectLoadError`, etc.)
- [ ] Add error recovery strategies

**5. Add Type Hints** (Day 4-5)
- [ ] Add type hints to all public methods in core/
- [ ] Run mypy: `pip install mypy && mypy core/`
- [ ] Fix type errors
- [ ] Add mypy to CI/CD

---

### Week 3: Architecture Improvements 🟢

**6. Refactor IDE Window** (Day 1-3)
- [ ] Extract `MenuManager` from `ide_window.py`
- [ ] Extract `ToolbarManager`
- [ ] Extract `ProjectActions`
- [ ] Update imports and test

**7. Document Architecture** (Day 4-5)
- [ ] Create `docs/architecture.md`
- [ ] Document signal flow
- [ ] Create component diagrams
- [ ] Write developer onboarding guide

---

## 8. Long-Term Improvements (Month 2-3)

### 8.1 Plugin System
- Create `plugins/` directory
- Define plugin API (action handlers, exporters, editors)
- Implement plugin discovery and loading
- Document plugin development

### 8.2 Performance Profiling
- Add performance monitoring
- Profile large project loading
- Optimize sprite loading (lazy loading)
- Benchmark game execution

### 8.3 User Experience
- Add progress bars for long operations
- Improve error messages (user-friendly)
- Add undo/redo system
- Create comprehensive user documentation

---

## 9. Code Metrics Summary

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| **Test Coverage** | 0% | 80%+ | 🔴 Critical |
| **Largest File** | 2,700 lines | <500 lines | 🔴 Critical |
| **Type Hint Coverage** | ~40% | 90%+ | 🟡 Medium |
| **Duplicate Code** | High (export/) | Minimal | 🔴 Critical |
| **Documentation** | Minimal | Comprehensive | 🟡 Medium |
| **Error Handling** | Inconsistent | Standardized | 🟡 Medium |

---

## 10. Conclusion

**PyGameMaker 2 is a solid foundation** with excellent architectural decisions (signal-based communication, clear layering, comprehensive GM8.0 compatibility). However, **technical debt has accumulated** in the form of:

1. **Monolithic files** that violate SRP
2. **Severe code duplication** in export modules
3. **Missing test infrastructure** preventing confident refactoring
4. **Production debugging code** cluttering output

**The good news:** These are all **solvable problems** with well-known solutions. By following the 3-week action plan above, the codebase can be transformed into a maintainable, testable, professional project ready for long-term development.

**Next Steps:**
1. Review this document with the team
2. Prioritize action items based on project goals
3. Start with Week 1 critical foundations
4. Establish coding standards going forward

**Questions or concerns?** Review each section and flag areas needing clarification.

---

**END OF REVIEW**
