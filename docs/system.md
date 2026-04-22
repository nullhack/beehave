# System Overview: beehave

> Last updated: 2026-04-22 — initial architecture (no features completed yet)

**Purpose:** beehave keeps Gherkin `.feature` files and Python test stubs in sync — assigning stable `@id` tags to Examples and generating/updating skipped test functions so living documentation and test scaffolding never diverge.

---

## Summary

beehave is a framework-agnostic CLI and Python library. Developers run `beehave sync` to reconcile their `.feature` files with their test suite: untagged Examples receive stable `@id` tags written back in-place, new stubs are created, changed stubs are updated, and orphaned stubs are flagged. A `beehave status` dry-run previews changes without writing anything. `beehave nest` bootstraps the canonical directory structure; `beehave hatch` generates demo content. The active test framework (default: pytest) is selected via `[tool.beehave]` in `pyproject.toml` or the `--framework` CLI flag.

---

## Actors

| Actor | Needs |
|-------|-------|
| Developer | Run `sync` to keep stubs current; run `status` in CI to gate on drift; run `nest` once per project |
| CI pipeline | `beehave status` exit codes (0 = in sync, 1 = drift); `--json` output for machine parsing |
| Framework author | `FrameworkAdapter` Protocol to supply stub conventions without forking beehave |

---

## Structure

| Module | Responsibility |
|--------|----------------|
| `beehave/` | Package root; public Python API surface |
| `beehave/cli/` | CLI entry points: `nest`, `sync`, `status`, `hatch`, `version` (uses `fire`) |
| `beehave/config/` | Read `[tool.beehave]` from `pyproject.toml`; apply defaults; merge CLI overrides |
| `beehave/parsing/` | Parse `.feature` files via `gherkin-official`; assign `@id` tags; derive slugs |
| `beehave/sync/` | Compute `SyncPlan`; execute create/update/move/warn operations on test stubs |
| `beehave/adapters/` | `FrameworkAdapter` Protocol + `PytestAdapter` concrete implementation |
| `beehave/cache/` | `FeatureCache` JSON persistence; stale/corrupt detection; incremental sync support |
| `beehave/scaffold/` | Create directory structure; inject `[tool.beehave]` into `pyproject.toml` |

---

## Key Decisions

- `.feature` files are the single source of truth; beehave only writes `@id` tags back to them — nothing else
- Test stub identity is the `@id` embedded in the function name (`test_<feature_slug>_<id>`); this is the only stable link between a stub and its Example
- Framework adapters are selected by config/flag, not auto-detected; default is `pytest`
- Stage subfolders (`backlog/`, `in-progress/`, `completed/`) are transparent to sync — all map to the same `tests/features/<slug>/` directory
- Orphan stubs are warned about but never deleted automatically
- `@deprecated` cascade is absolute in v1: Feature/Rule `@deprecated` propagates to all child Examples with no per-Example override
- Cache is invisible to users; auto-rebuilt if missing, stale, or corrupt
- See ADR-2026-04-22-feature-file-write-policy, ADR-2026-04-22-adapter-protocol, ADR-2026-04-22-id-stability, ADR-2026-04-22-error-handling-policy

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
- `beehave` never deletes files (stubs, feature files, or cache) automatically
- Config file location is always `pyproject.toml` in the current working directory
- v1 supports only the `pytest` adapter; `unittest` is parked for v2
- `@id` values are unique project-wide; collision on generation triggers silent retry
- Malformed `@id` tags (empty or non-hex) are replaced, not preserved
- Scenario Outline column changes produce a warning only — parametrize decorator is never auto-modified
- Custom template folder is a full replacement for built-in templates (not a merge)

---

## Relevant ADRs

- `ADR-2026-04-22-feature-file-write-policy` — `.feature` files are write-once for `@id` tags only
- `ADR-2026-04-22-adapter-protocol` — FrameworkAdapter as a structural Protocol (not ABC)
- `ADR-2026-04-22-id-stability` — `@id` assignment and collision policy
- `ADR-2026-04-22-error-handling-policy` — error vs. warn policy for deletions, duplicates, malformed config
- `ADR-2026-04-22-slug-derivation` — slug derivation is stage-folder-independent

---

## Completed Features

*(none — initial architecture pass)*
