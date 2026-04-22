# System Overview: beehave

> Last updated: 2026-04-22 — architecture design session 1 (no features completed yet)

**Purpose:** beehave keeps Gherkin `.feature` files and Python test stubs in sync — assigning stable `@id` tags to Examples and generating/updating skipped test functions so living documentation and test scaffolding never diverge.

---

## Summary

beehave is a framework-agnostic CLI and Python library. Developers run `beehave sync` to reconcile their `.feature` files with their test suite: untagged Examples receive stable `@id` tags written back in-place using surgical line insertion, new stubs are created, changed stubs are updated, and orphaned stubs are flagged. A `beehave status` dry-run previews changes without writing anything. `beehave nest` bootstraps the canonical directory structure; `beehave hatch` generates demo content. The active test framework (default: pytest) is selected via `[tool.beehave]` in `pyproject.toml` or the `--framework` CLI flag.

---

## Actors

| Actor | Needs |
|-------|-------|
| Developer | Run `sync` to keep stubs current; run `status` in CI to gate on drift; run `nest` once per project |
| CI pipeline | `beehave status` exit codes (0 = in sync, 1 = drift); `--json` output for machine parsing |
| Framework author | `FrameworkAdapter` Protocol to supply stub conventions without importing from beehave |

---

## Structure

| Module | Responsibility |
|--------|----------------|
| `beehave/` | Package root; public Python API surface |
| `beehave/cli/` | Entry points: `nest`, `sync`, `status`, `hatch`, `version` (composition root; uses `fire`) |
| `beehave/config/` | Read `[tool.beehave]` from `pyproject.toml`; apply defaults; merge CLI overrides |
| `beehave/parsing/` | Parse `.feature` files via `gherkin-official`; assign `@id` tags (surgical insertion); derive slugs; manage incremental cache |
| `beehave/sync/` | Compute `SyncPlan`; execute create/update/move/warn operations on test stubs |
| `beehave/adapters/` | `FrameworkAdapter` Protocol + `PytestAdapter` concrete implementation |
| `beehave/nest/` | Create directory structure; inject `[tool.beehave]` into `pyproject.toml` |

---

## Key Decisions

- `.feature` files are the single source of truth; beehave only writes `@id` tags back to them using surgical line insertion — nothing else is touched
- Test stub identity is the `@id` embedded in the function name (`test_<feature_slug>_<id>`); this is the only stable link between a stub and its Example
- Framework adapters are selected by config/flag, not auto-detected; default is `pytest`; defined as `typing.Protocol` (zero import coupling for third-party adapters)
- Stage subfolders (`backlog/`, `in-progress/`, `completed/`) are transparent to sync — all map to the same `tests/features/<slug>/` directory
- Orphan stubs are warned about (or error, per `on_orphan` config) but never deleted automatically
- Duplicate `@id` values found in files is always a hard error — no safe resolution exists
- `@deprecated` cascade is absolute in v1: Feature/Rule `@deprecated` propagates to all child Examples with no per-Example override
- Cache is invisible to users; auto-rebuilt if missing, stale, or corrupt; full scan is the correctness baseline
- Absent `pyproject.toml` uses defaults (no error); malformed `pyproject.toml` is always a hard error
- Standard Python `logging` module; four levels (DEBUG/INFO/WARNING/ERROR); default WARNING; configurable via `log_level`

---

## Configuration Keys (`[tool.beehave]`)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `framework` | string | `"pytest"` | Test framework adapter to use |
| `features_dir` | string | `"docs/features"` | Root directory for `.feature` files |
| `template_path` | string | `null` | Custom template folder (fully replaces built-in) |
| `log_level` | string | `"WARNING"` | Log level: DEBUG / INFO / WARNING / ERROR |
| `on_delete` | string | `"warn"` | Policy when a `.feature` file is deleted: `"warn"` or `"error"` |
| `on_orphan` | string | `"warn"` | Policy for orphan stubs (no matching `@id`): `"warn"` or `"error"` |

---

## External Dependencies

| Dependency | What it provides | Why not replaced |
|------------|------------------|-----------------|
| `gherkin-official` | Gherkin parser (AST from `.feature` files) | Official Cucumber parser; handles all Gherkin edge cases correctly |
| `fire` | CLI argument parsing and dispatch | Zero-boilerplate CLI from Python functions; matches beehave's simple command surface |

---

## Active Constraints

- No auto-detection of test framework — explicit config or flag required
- No watch mode, no pre-commit hooks, no auto-triggers — on-demand only
- Test bodies are never modified under any circumstance
- beehave never deletes files (stubs, feature files, or cache) automatically
- Config file location is always `pyproject.toml` in the current working directory; absent = use defaults
- v1 supports only the `pytest` adapter; `unittest` is parked for v2
- `@id` values are unique project-wide; collision on generation triggers silent retry; duplicate `@id` in files → hard error
- Malformed `@id` tags (empty or non-hex) are replaced in-place using surgical line scan
- Feature file rename is not detectable — old test directory becomes an orphan; developer migrates manually
- Scenario Outline column changes produce a warning only — parametrize decorator is never auto-modified
- Custom template folder is a full replacement for built-in templates (not a merge)
- Cache is optimisation-only at target scale (100–1,000 Examples); full-scan fallback is always correct

---

## Relevant ADRs

| ADR | Decision |
|-----|----------|
| `ADR-2026-04-22-feature-file-write-policy` | `.feature` files are write-once for `@id` tags only; surgical line insertion |
| `ADR-2026-04-22-adapter-protocol` | `FrameworkAdapter` as a structural `typing.Protocol` (not ABC) |
| `ADR-2026-04-22-id-stability` | `@id` assignment, collision policy, duplicate = hard error |
| `ADR-2026-04-22-error-handling-policy` | Error vs. warn policy per condition; `on_delete` and `on_orphan` config keys |
| `ADR-2026-04-22-slug-derivation` | Slug from file stem only; stage-folder-independent; rename = orphan |
| `ADR-2026-04-22-module-structure` | 6 submodules: cli, config, parsing, sync, adapters, nest |
| `ADR-2026-04-22-performance-targets` | Target scale medium (100–1k Examples); cache is optimisation not load-bearing |
| `ADR-2026-04-22-backwards-compatibility` | Best-effort warn-before-remove; no hard semver guarantee |
| `ADR-2026-04-22-logging-observability` | Standard Python logging; 4 levels; `log_level` config key + `--log-level` flag |

---

## Completed Features

*(none — implementation not yet started)*
