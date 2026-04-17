# Discovery: plugin-hook

## State
Status: BASELINED

## Entities
| Type | Name | Candidate Class/Method | In Scope |
|------|------|----------------------|----------|
| Noun | pytest plugin | `BeehavePlugin` | Yes |
| Noun | pytest session | pytest lifecycle | Yes |
| Noun | pytest config | `pytest_configure` hook | Yes |
| Noun | stub sync | full sync operation | Yes |
| Verb | register plugin | `pytest_configure` entry point | Yes |
| Verb | run before collection | `pytest_sessionstart` or `pytest_collection_start` | Yes |
| Verb | trigger stub sync | invoke sync logic before collection | Yes |

## Rules
- The plugin registers itself automatically via `entry_points` in `pyproject.toml` — no manual `conftest.py` required
- The stub sync runs before pytest collection so that any newly generated stubs are discovered and collected in the same `pytest` invocation
- The plugin is always-on; there is no configuration option to disable it

## Constraints
- Must not break pytest collection if the features directory does not exist or is empty
- Must be compatible with pytest ≥ 6.0
- Entry point key: `pytest11`

## Questions
| ID | Question | Answer | Status |
|----|----------|--------|--------|
| Q1 | Which pytest hook runs before collection? | `pytest_configure` runs at startup before collection; `pytest_sessionstart` runs after collection starts — use `pytest_configure` or a custom `pytest_collection_start` hook | ANSWERED |
| Q2 | Should the plugin emit any output to the pytest terminal during sync? | Yes — brief summary of actions taken (same style as current script) | ANSWERED |

## Architecture

### Module Structure

```
pytest_beehave/
├── config.py    (existing) — resolve_features_path(rootdir) → Path
├── plugin.py    (extend)   — add pytest_sessionstart hook; pytest_configure stays as-is
└── syncer.py    (new)      — sync_stubs(features_dir, tests_dir) → list[str]; pure sync logic
```

| File | Responsibility |
|------|---------------|
| `pytest_beehave/syncer.py` | Pure sync logic: scan feature folders, create/update test stubs, return action list |
| `pytest_beehave/plugin.py` | Add `pytest_sessionstart` hook: get stashed path, call `sync_stubs`, write actions to terminal |

### Key Signatures

```python
# pytest_beehave/syncer.py

def sync_stubs(features_dir: Path, tests_dir: Path) -> list[str]:
    """Sync test stubs from .feature files to tests/features/.

    Scans features_dir for backlog/, in-progress/, and completed/ sub-folders.
    Creates or updates test stub files under tests_dir/<feature-name>/.
    Returns a list of human-readable action strings (e.g. "CREATE ...", "ADD stub ...").

    Args:
        features_dir: Root of the features directory (contains backlog/, in-progress/, completed/).
        tests_dir: Root of the tests/features/ directory where stubs are written.

    Returns:
        List of action description strings. Empty list if nothing changed.
    """
```

```python
# pytest_beehave/plugin.py (addition)

def pytest_sessionstart(session: pytest.Session) -> None:
    """Run stub sync before test collection begins.

    Reads the stashed features path, syncs test stubs, and reports
    actions to the terminal. Warns and skips if the features directory
    is absent.

    Args:
        session: The pytest Session object.
    """
```

### Data Flow

```
pytest invoked
      │
      ▼
pytest_configure(config)          [plugin.py — existing]
      │  resolve_features_path(rootdir) → path
      │  path.exists()? NO → pytest.exit() [only if explicitly configured]
      │  YES → config.stash[features_path_key] = path
      │
      ▼
pytest_sessionstart(session)      [plugin.py — NEW hook]
      │
      ├─ features_dir = session.config.stash[features_path_key]
      │
      ├─ features_dir.exists()?
      │     NO  → terminal.write_line("[beehave] warning: features dir not found, skipping sync")
      │           return (no crash)
      │     YES → tests_dir = session.config.rootpath / "tests" / "features"
      │           actions = sync_stubs(features_dir, tests_dir)
      │           write actions to terminal via session.config.get_terminal_writer()
      │
      ▼
pytest collection begins (newly created stubs are now on disk → collected)
      │
      ▼
tests run
```

### Key Decisions (ADRs)

#### ADR-001: Use `pytest_sessionstart` as the sync hook

**Decision**: Run stub sync in `pytest_sessionstart`, not `pytest_configure` or `pytest_collection`.

**Reason**: `pytest_sessionstart` is called "after the Session object has been created and before performing collection" (pytest hookspec). This is exactly the window needed: after `pytest_configure` has stashed the features path, and before any test files are collected. `pytest_configure` runs too early (no Session, no terminal writer). `pytest_collection_modifyitems` runs after collection — too late.

**Alternatives considered**:
- `pytest_configure` — rejected: no `Session` object, no terminal writer, runs before stash is populated in the same hook
- `pytest_collection` hook wrapper — rejected: more complex, requires `hookwrapper=True`; `pytest_sessionstart` is simpler and sufficient
- `pytest_collection_modifyitems` — rejected: runs after collection; new stubs would not be collected in the same run

---

#### ADR-002: Extract sync logic into `syncer.py`

**Decision**: Create `pytest_beehave/syncer.py` with a single public function `sync_stubs(features_dir, tests_dir) → list[str]`. The plugin calls this function.

**Reason**: SOLID-S — `plugin.py` owns pytest hook wiring; `syncer.py` owns stub sync logic. The sync logic is non-trivial (Gherkin parsing, file I/O, stub generation) and deserves its own module. This also makes `syncer.py` independently testable without pytest fixtures.

**Alternatives considered**:
- Inline sync logic in `plugin.py` — rejected: violates SOLID-S; `plugin.py` would have two reasons to change
- Import from `.opencode/skills/tdd/scripts/gen_test_stubs.py` — rejected: production code must not import from developer tooling scripts; the script has hardcoded paths and is not a package
- Subprocess call to `uv run task gen-tests` — rejected: subprocess adds latency, requires `uv` on PATH, and makes testing harder

---

#### ADR-003: Terminal output via `config.get_terminal_writer()`

**Decision**: Write sync output using `session.config.get_terminal_writer()`.

**Reason**: This is the pytest-idiomatic way to write to the terminal. It respects pytest's output capture settings (`-s`, `-q`, `--capture`). `print()` would bypass capture and always appear, which is incorrect behaviour in quiet mode.

**Alternatives considered**:
- `print()` — rejected: bypasses pytest capture; always visible even with `-q`
- `warnings.warn()` — rejected: wrong abstraction; warnings are for Python-level deprecation notices, not plugin status messages

---

#### ADR-004: `tests_dir` derived from `rootpath`, not stashed

**Decision**: Derive `tests_dir = session.config.rootpath / "tests" / "features"` in `pytest_sessionstart`, not stored in stash.

**Reason**: YAGNI — the tests directory is always `tests/features/` relative to the project root. There is no AC requiring it to be configurable. Computing it from `rootpath` is one line and needs no stash key.

**Alternatives considered**:
- Add `tests_dir` to `[tool.beehave]` config — rejected: YAGNI; no AC requires this
- Stash `tests_dir` in `pytest_configure` — rejected: unnecessary indirection

---

### ⚠️ Spec Contradiction — Requires PO Resolution

**Conflict between `plugin-configuration @id:124f65e7` and `plugin-hook @id:e3a13b58`:**

- `plugin-configuration @id:124f65e7` (already implemented): "pytest fails with hard error when configured features path does not exist" → current `plugin.py` calls `pytest.exit()` if `path.exists()` is False
- `plugin-hook @id:e3a13b58`: "Plugin does not crash when features directory is absent" → "pytest completes collection without errors"

These directly contradict each other. The current implementation will `pytest.exit()` before `pytest_sessionstart` even runs, so `e3a13b58` can never pass as written.

**Proposed resolution (for PO decision):**

Option A — Narrow the hard error: `pytest.exit()` only when `features_path` is **explicitly configured** in `[tool.beehave]` AND the path doesn't exist. If using the **default** path and it doesn't exist → warn and continue (satisfies `e3a13b58`).

Option B — Remove the hard error from `pytest_configure` entirely: always stash the path regardless of existence; let `pytest_sessionstart` decide whether to warn or error based on whether the path was explicitly configured.

Option C — Keep hard error as-is, and interpret `e3a13b58` as "the features directory exists but is empty" (not "does not exist"). This would require changing the feature file wording.

**Developer recommendation**: Option A. It preserves the intent of both ACs: explicit misconfiguration → hard error; missing default directory → graceful degradation.

---

### Build Changes

**New runtime dependency**: `gherkin-official` — required by `syncer.py` for Gherkin parsing. Currently in `[dependency-groups] dev` only. **Needs PO approval** to move to `[project] dependencies`.

**New file**: `pytest_beehave/syncer.py` — no `pyproject.toml` changes beyond the dependency.

**Modified file**: `pytest_beehave/plugin.py` — add `pytest_sessionstart` hook.

**Possible modification**: `pytest_beehave/plugin.py` `pytest_configure` — may need to change hard-error behavior depending on PO resolution of spec contradiction above.
