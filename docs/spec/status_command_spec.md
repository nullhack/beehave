# beehave status — Command Specification

**Author:** System Architect (revised by PO 2026-05-19)
**Date:** 2026-05-19
**Status:** Finalized
**Supersedes:** Original Draft (SA, 2026-05-19)
**Authoritative:** domain_spec.md § Status Reporting

---

## 1. Overview

The `beehave status` command reports the development stage of each feature in the project. Stages are derived entirely from data already computable by the existing codebase: Gherkin parsing (`parse_feature()`), test discovery (`discover_tests()`), and consistency checking (`check_pair()`). No new parsing or heuristic logic is needed — the command is a **presentation layer** over existing infrastructure.

---

## 2. Stage Taxonomy

### 2.1 Feature Stages

A feature (`.feature` file) is in exactly one of seven stages. The decision tree is evaluated in priority order — the first matching condition determines the stage.

#### Decision Tree

| Priority | Condition | Stage |
|----------|-----------|-------|
| 1 | `parse_feature()` raises `GherkinError` | `broken` |
| 2 | `parse_feature()` returns `{}` (0 scenarios) | `no scenarios` |
| 3 | Feature has Rules but every Rule has zero Scenarios | `needs scenarios` |
| 4 | Any scenario has no matching test function (`ti is None`) | `needs tests` |
| 5 | All scenarios mapped AND any matched test is a stub (`ti.is_stub`) | `needs bodies` |
| 6 | All scenarios mapped, all non-stub, AND any `check_pair()` violation (errors only) | `needs fixes` |
| 7 | All scenarios mapped, all non-stub, zero violations | `ok` |

#### Stage Definitions

| Stage | Meaning | Next Action |
|-------|---------|-------------|
| `broken` | Feature file is syntactically or semantically broken (bad Gherkin, duplicate function name, invalid title, etc.) | Fix the `.feature` file |
| `no scenarios` | Feature file parses but contains no Scenario or Scenario Outline children | Add scenarios or delete the file |
| `needs scenarios` | Feature has Rule blocks but no Scenarios inside any Rule | Add Scenarios to existing Rules |
| `needs tests` | One or more scenarios have no matching test function | Run `beehave generate <feature>` |
| `needs bodies` | Every scenario has a test function, but at least one is a stub | Replace stub bodies with real test logic |
| `needs fixes` | All tests are non-stub, but at least one has violations | Fix the implementation |
| `ok` | All scenarios mapped, all tests non-stub, zero violations | None — feature is complete |

### 2.2 Scenario Status (per-scenario granularity)

| Status | Criteria |
|--------|----------|
| `no test` | No matching test function exists |
| `no body` | Matching test exists with stub body (`pass` / `...`) |
| `N errors` | Non-stub test with N violations from `check_pair()` |
| `ok` | Non-stub test with zero violations |

The feature stage is the "worst" scenario status: `no test` > `no body` > `N errors` > `ok`.

### 2.3 Non-Feature Artifacts

#### Unmapped Test Directories

A test directory (`tests/features/<slug>/`) with no corresponding `.feature` file. Reported separately when `--include-unmapped` is used.

---

## 3. Edge Case Resolution

### 3.1 Malformed Feature File

Call `parse_feature()` inside a try/except. On `GherkinError`, mark the feature as `broken`. Include the error message in verbose output. Do NOT crash or skip silently.

### 3.2 Empty Feature File

`parse_feature()` raises `GherkinError`. Treat as `broken`.

### 3.3 Feature With Zero Scenarios

`parse_feature()` returns `{}`. Stage = `no scenarios`.

### 3.4 Feature With Rules But No Scenarios

`parse_feature()` returns `{}` but Gherkin AST has Rule nodes with zero Scenario children. Stage = `needs scenarios`. Distinct from `no scenarios` — the feature has Rule structure, just no testable content inside those Rules.

### 3.5 Feature File Changed After Generation

- Renamed scenario → old test is now unmapped. Feature stage → `needs tests`.
- Added placeholder → `missing-placeholder` violation. If test was non-stub → `needs fixes`.
- Stubs mask violations — a feature can go `needs tests` → `needs bodies` → `needs fixes` as stubs get implemented.

### 3.6 Mixed-Status Feature

Feature stage = worst scenario status. A feature with 2 ok, 1 no body, 1 no test → `needs tests`.

### 3.7 Cross-Feature Function Name Collision

Parse features independently (no shared `seen_fn`). Detect collisions in post-processing. Collisions are warnings — they do not degrade the stage.

### 3.8 Misplaced Test

Test in wrong directory still matches its scenario by `function_name`. Generates a `misplaced-test` warning. Warnings do not affect the feature stage.

### 3.9 Scenario Outline With Incomplete Example Coverage

`check_pair()` produces `example-mismatch` violations. Non-stub test → stage `needs fixes`. Stub test → mismatches not checked.

---

## 4. Output Format Specification

### 4.1 Default: Tree Hierarchy

Tree-based format showing Feature → Rule → Scenario. Status labels in a fixed-width left column. Plain text labels, no symbols.

```
needs fixes     hive_activity (Hive Activity)
  ok            ├── honey production from nectar           (3 ex)
  2 errors      ├── Hive defense
  2 errors      │   ├── guard bee inspects visitor         scent, floral
  no body       │   └── guard bee inspects visitor2
  ok            └── Foraging
  ok                └── forager returns with nectar

  ok            comb_construction (Comb Construction)

needs bodies    dance_language (Waggle Dance Communication)
  no body       ├── round dance
  no body       └── waggle dance

no scenarios    future_ideas (Future Ideas)

needs scenarios temperature_control (Temperature Control)
  no scenarios  ├── Heating
  no scenarios  ├── Cooling
  no scenarios  └── Ventilation
```

**Format rules:**
- Status column on left, fixed-width (padded to longest status label)
- Tree characters (`├──`, `│`, `└──`) for hierarchy
- `ok` features collapse to one line — no tree expansion
- Rule aggregate shows breakdown of child statuses with counts (`2 errors`, `1 error, 1 no body`)
- Scenario Outlines show example count: `(N ex)`
- Failing scenarios show violation codes inline after the scenario name
- `no scenarios` for features with no children; `needs scenarios` for features with Rules but no Scenarios
- `--json` flag outputs full JSON with feature/scenario hierarchy, counts, and violation details

### 4.2 JSON Output (`--json`)

```json
{
  "features": [
    {
      "path": "hive_activity",
      "title": "Hive Activity",
      "stage": "needs fixes",
      "scenarios_total": 4,
      "scenarios_ok": 2,
      "scenarios_errors": 1,
      "scenarios_no_body": 1,
      "scenarios_no_test": 0,
      "violations_error_count": 2,
      "violations_warning_count": 0,
      "parse_error_message": null,
      "scenarios": [
        {
          "title": "guard bee inspects visitor",
          "function_name": "test_guard_bee_inspects_visitor",
          "status": "2 errors",
          "is_stub": false,
          "is_outline": false,
          "line": 23,
          "violations": [
            {"path": "...", "line": 23, "error_type": "missing-placeholder", "message": "'scent' not found", "is_warning": false}
          ]
        }
      ]
    }
  ],
  "unmapped_directories": [],
  "collisions": [],
  "summary": {
    "total_features": 2,
    "broken": 0,
    "no_scenarios": 0,
    "needs_scenarios": 0,
    "needs_tests": 0,
    "needs_bodies": 1,
    "needs_fixes": 1,
    "ok": 0
  }
}
```

### 4.3 Color / ANSI Rules

| Stage | Color | ANSI |
|-------|-------|------|
| `ok` | Green | `\033[32m` |
| `needs fixes` | Red | `\033[31m` |
| `needs bodies` | Yellow | `\033[33m` |
| `needs tests` | Magenta | `\033[35m` |
| `needs scenarios` | Blue | `\033[34m` |
| `broken` | Red bold | `\033[1;31m` |
| `no scenarios` | Dim | `\033[2m` |

**Color control:** Auto-detect `sys.stdout.isatty()`. Environment variable fallback: `NO_COLOR` / `FORCE_COLOR`.

---

## 5. CLI Interface

### 5.1 Command Signature

```
beehave status [feature] [options]
```

### 5.2 Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `feature` | positional, optional | Feature path slug (without extension). When provided, shows status for only that feature. When omitted, shows status for all features. |

### 5.3 Options

| Flag | Description |
|------|-------------|
| `--json` | Output machine-readable JSON to stdout. |
| `--include-unmapped` | Show unmapped test directories. |

### 5.4 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All features are `ok` (or `no scenarios`/`needs scenarios`, or no features exist) |
| 1 | At least one feature is `broken`, `needs tests`, `needs bodies`, or `needs fixes` |
| 2 | Fatal error: features directory not found, disk I/O error, unhandled exception |

### 5.5 Examples

```bash
$ beehave status                                    # Show all features
$ beehave status hive_activity                      # Single feature
$ beehave status --json | jq '.summary'             # Machine-readable
$ beehave status --include-unmapped                 # Include unmapped test dirs
```

### 5.6 Stderr Usage

- ALL output (table, JSON, summary) goes to **stdout**.
- **stderr** is used only for fatal runtime errors.
- `broken` features are reported in stdout as part of the table, NOT on stderr.

---

## 6. Implementation Strategy

### 6.1 New Module: `beehave/status.py`

```
beehave/status.py
├── ScenarioStatus dataclass
├── FeatureStatus dataclass
├── StatusReport dataclass
├── compute_scenario_status()    # ScenarioInfo + TestInfo + Violations → ScenarioStatus
├── compute_feature_status()     # Feature path → FeatureStatus (parses, discovers, checks)
├── compute_all_status()         # All features → StatusReport
├── format_tree()                # StatusReport → str (tree-based output)
├── format_json()                # StatusReport → str (JSON)
└── format_summary()             # StatusReport → str (summary footer)
```

### 6.2 Changes to Existing Modules

**`beehave/models.py`** (+3 dataclasses):
```python
@dataclass(frozen=True)
class ScenarioStatus:
    title: str
    function_name: str
    status: str
    is_stub: bool
    is_outline: bool
    line: int
    violations: tuple[Violation, ...]

@dataclass(frozen=True)
class FeatureStatus:
    path: str
    title: str
    stage: str
    scenarios_total: int
    scenarios_ok: int
    scenarios_errors: int
    scenarios_no_body: int
    scenarios_no_test: int
    violations_error_count: int
    violations_warning_count: int
    parse_error_message: str | None
    scenarios: tuple[ScenarioStatus, ...]

@dataclass(frozen=True)
class StatusReport:
    features: tuple[FeatureStatus, ...]
    unmapped_directories: tuple[dict, ...]
    collisions: tuple[dict, ...]
    summary: dict[str, int]
```

**`beehave/cli.py`** (+~50 lines): Add `cmd_status(args)` and `status` subparser.

**Unchanged:** `gherkin.py`, `discover.py`, `check.py`, `config.py`, `generate.py`, `clean.py`

### 6.3 Files Affected

- **New:** `beehave/status.py` (~300 lines)
- **Modified:** `beehave/models.py` (+3 dataclasses, ~70 lines), `beehave/cli.py` (+~50 lines)
- **Unchanged:** Everything else
- **New tests:** `tests/test_status.py` (~400 lines), additions to `tests/test_cli.py` (~100 lines)

---

## 7. Design Decisions Not Made Here

- **Caching:** No file-mtime-based caching in v1
- **Parallel parsing:** No `concurrent.futures` in v1
- **Historical status tracking:** No `--since <commit>` or trend reporting
- **Watch mode:** No `--watch` flag
- **Auto-fix suggestions:** Status describes state, does not suggest corrective actions

---

## 8. Summary

The `beehave status` command is a pure presentation layer over existing infrastructure. The seven-stage taxonomy maps directly to existing violation types from `check_pair()`. The decision tree is unambiguous. The tree-based output format mirrors the Gherkin hierarchy naturally.

**Key design principles:**
- All stage names and status labels are plain English — no symbols, no jargon, no legend needed
- Tree format mirrors the Gherkin parse tree: Feature → Rule → Scenario
- `ok` features collapse to one line for maximum scan efficiency
- Status on the left in a fixed column for vertical scanning
- Parse errors are first-class stages, not side-channel stderr
- Warnings don't block `ok`
- Exit codes mirror `beehave check`: Exit 1 = work to do, Exit 0 = clean
