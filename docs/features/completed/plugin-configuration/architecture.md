# Architecture: plugin-configuration

## Module Layout

```
pytest_beehave/
├── __init__.py          # package stub (unchanged)
├── __main__.py          # CLI entry point (unchanged)
├── config.py            # NEW — reads [tool.beehave] from pyproject.toml, resolves features_path
└── plugin.py            # NEW — pytest plugin entry point; registers pytest_configure hook
```

### File responsibilities (one line each)

| File | Responsibility |
|------|---------------|
| `pytest_beehave/config.py` | Pure function: locate `pyproject.toml`, parse `[tool.beehave].features_path`, return resolved `pathlib.Path` |
| `pytest_beehave/plugin.py` | pytest plugin: `pytest_configure` hook reads config and stores resolved path on `config` object; hard-errors if path missing |

---

## Key Signatures

### `pytest_beehave/config.py`

```python
from pathlib import Path


DEFAULT_FEATURES_PATH: str = "docs/features/"


def resolve_features_path(rootdir: Path) -> Path:
    """Resolve the features directory path from pyproject.toml or use the default.

    Reads [tool.beehave].features_path from pyproject.toml located at rootdir.
    Falls back to docs/features/ if pyproject.toml is absent or has no [tool.beehave]
    section.  Does NOT validate existence — that is the caller's responsibility.

    Args:
        rootdir: Absolute path to the project root (directory containing pyproject.toml).

    Returns:
        Resolved absolute Path to the features directory.
    """
```

### `pytest_beehave/plugin.py`

```python
import pytest
from pathlib import Path
from pytest_beehave.config import resolve_features_path


def pytest_configure(config: pytest.Config) -> None:
    """Read beehave configuration and store the resolved features path.

    Resolves the features directory from pyproject.toml.  Exits pytest with a
    hard error if the configured path does not exist on disk.

    Args:
        config: The pytest Config object (provides rootdir and stash).
    """
```

---

## Data Flow

```
pytest invoked
      │
      ▼
pytest_configure(config)          [plugin.py]
      │
      ├─ rootdir = Path(config.rootdir)
      │
      ▼
resolve_features_path(rootdir)    [config.py]
      │
      ├─ pyproject.toml present?
      │     YES → parse with tomllib
      │           [tool.beehave].features_path present?
      │                 YES → rootdir / configured_path  ──┐
      │                 NO  → rootdir / "docs/features/" ──┤
      │     NO  → rootdir / "docs/features/"  ────────────┘
      │
      ▼
      resolved: Path  (absolute, not yet validated)
      │
      ▼
back in pytest_configure:
      │
      ├─ resolved.exists()?
      │     YES → store on config (config.stash[features_path_key] = resolved)
      │     NO  → pytest.exit(f"[beehave] features_path not found: {resolved}", returncode=1)
      │
      ▼
pytest collection proceeds (reads features_path from config.stash)
```

---

## Design Decisions (ADRs)

### ADR-001: Use stdlib `tomllib` (no new runtime dependency)

**Decision**: Parse `pyproject.toml` with `tomllib` from the Python 3.13 standard library.

**Reason**: The project already requires Python ≥ 3.13 (`pyproject.toml: requires-python = ">=3.13"`), so `tomllib` is always available — no new runtime dependency needed.

**Alternatives considered**:
- `tomli` (backport) — rejected: unnecessary dependency when stdlib covers it.
- pytest's `Config.getini()` — rejected: `[tool.beehave]` is not a pytest ini option; using `getini` would require registering a custom ini option, which is more complexity than needed (KISS violation).

**Build changes needed**: None. No new runtime dependency.

---

### ADR-002: Single pure function in `config.py`, no class

**Decision**: `resolve_features_path(rootdir: Path) -> Path` — one function, no class, no config object.

**Reason**: The feature has exactly one configurable value (`features_path`). A class would be YAGNI. A pure function is testable in isolation without any pytest machinery.

**Alternatives considered**:
- `BeehaveConfig` dataclass — rejected: over-engineering for a single field (YAGNI).
- Returning `str` — rejected: `Path` is the correct type for filesystem paths; callers should not need to convert.

---

### ADR-003: `pytest_configure` as the integration hook

**Decision**: Read configuration in `pytest_configure`, store the resolved path in `config.stash`.

**Reason**: `pytest_configure` runs before collection, which is required by the project-level discovery (Q11: "Sync BEFORE collection"). `config.stash` is the pytest-idiomatic way to pass data between hooks without global state.

**Alternatives considered**:
- `pytest_sessionstart` — rejected: runs after collection begins; too late.
- Module-level global — rejected: not thread-safe and violates SOLID-D (couples modules to global state).
- Fixture — rejected: fixtures are per-test, not per-session; wrong granularity.

---

### ADR-004: Hard error via `pytest.exit()`, not `raise`

**Decision**: When the configured path does not exist, call `pytest.exit(msg, returncode=1)`.

**Reason**: AC `@id:124f65e7` requires "pytest run exits with a non-zero status code and an error naming the missing path". `pytest.exit()` produces a clean, user-readable exit with the exact message — no traceback noise. `raise SystemExit` or `raise ValueError` would produce confusing output.

**Alternatives considered**:
- `raise FileNotFoundError` — rejected: produces a traceback, not a clean error message.
- `config.warn()` — rejected: AC explicitly requires a hard error (non-zero exit), not a warning.

---

### ADR-005: `plugin.py` as the pytest entry point (separate from `config.py`)

**Decision**: Split pytest hook registration (`plugin.py`) from config logic (`config.py`).

**Reason**: SOLID-S — `config.py` has one reason to change (config parsing logic); `plugin.py` has one reason to change (pytest hook wiring). This also makes `config.py` testable without any pytest fixtures.

**Alternatives considered**:
- Single `plugin.py` with everything — rejected: mixes I/O concerns (TOML parsing) with pytest lifecycle concerns.
- Putting hooks in `__init__.py` — rejected: `__init__.py` is a package stub; mixing plugin registration there violates SOLID-S.

---

## YAGNI Check

The 3 acceptance criteria require exactly:
1. Read `features_path` from `[tool.beehave]` → use it ✓
2. Fall back to `docs/features/` when absent → use default ✓
3. Hard error when configured path doesn't exist ✓

**Not in scope** (explicitly excluded):
- Registering the plugin via `entry_points` in `pyproject.toml` — that is `plugin-hook` feature territory
- Any other `[tool.beehave]` keys (e.g., `ci_mode`, `output_path`) — YAGNI
- Caching the resolved path — YAGNI (called once per session)
- Validating that `features_path` is a string — YAGNI (TOML type system handles this; a non-string would be a TOML parse error)

---

## Contradiction Check (ADRs vs. Acceptance Criteria)

| ADR | AC | Verdict |
|-----|----|---------|
| ADR-001: `tomllib` | `@id:acf12157`, `@id:ce8a95e7` | No contradiction — TOML parsing is the correct mechanism |
| ADR-002: pure function | All 3 | No contradiction — function returns `Path` used by all 3 paths |
| ADR-003: `pytest_configure` | All 3 | No contradiction — hook runs before collection as required |
| ADR-004: `pytest.exit()` | `@id:124f65e7` | No contradiction — produces non-zero exit with named path |
| ADR-005: split modules | All 3 | No contradiction — structural only |

**No contradictions found.**

---

## Build Changes

**New runtime dependency**: None.

**New files**: `pytest_beehave/config.py`, `pytest_beehave/plugin.py` — both are source files within the existing package; no `pyproject.toml` changes required for this feature.

> Note: Registering the plugin via `[project.entry-points]` in `pyproject.toml` is part of the `plugin-hook` feature, not this one. This feature only covers configuration reading.
