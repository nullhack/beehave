# ADR: Package module structure — six bounded contexts

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | all |
| **Status** | Accepted (supersedes speculative v0 from same date) |

## Context

**Question (D1):** How should the `beehave` package be organized into submodules?

Initial proposal was 7 submodules (with separate `scaffold` and `cache` modules). Two problems: (1) "scaffold" has no place in the bee-themed vocabulary — the CLI command is `nest`; the submodule must match; (2) `cache` has no independent public API — it exists solely to serve `parsing`, making it a sub-file, not a separate module. Six submodules was confirmed as the minimum necessary for clear single-responsibility boundaries.

---

## Decision

The `beehave` package is organized into **six submodules**:

| Submodule | Responsibility |
|-----------|----------------|
| `beehave/cli/` | Entry points: `nest`, `sync`, `status`, `hatch`, `version` (composition root) |
| `beehave/config/` | Read `[tool.beehave]` from `pyproject.toml`; apply defaults; merge CLI overrides |
| `beehave/parsing/` | Parse `.feature` files; assign `@id` tags; derive slugs; cache incremental state |
| `beehave/sync/` | Compute `SyncPlan`; execute create/update/move/warn on test stubs |
| `beehave/adapters/` | `FrameworkAdapter` Protocol + `PytestAdapter` concrete implementation |
| `beehave/nest/` | Create directory structure; inject `[tool.beehave]` into `pyproject.toml` |

## Reason

The initial 7-submodule design (with separate `scaffold` and `cache` modules) was rejected for two reasons:
1. **Branding misalignment**: "scaffold" has no place in the bee-themed vocabulary. The CLI command is `nest`; the submodule should match.
2. **Over-granularity**: `cache` has no independent public API — it exists solely to serve `parsing`. Merging it into `parsing` reduces import surface and cognitive overhead without losing encapsulation.

Six submodules is the minimum necessary for clear single-responsibility boundaries.

## Alternatives Considered

- **7 submodules (separate `cache` + `scaffold`)**: rejected — see above
- **3 layers (core/adapters/cli)**: rejected — too coarse; `parsing` and `sync` have different change rates and external dependencies
- **Flat package**: rejected — 14 features across 6 concerns; flat structure would produce an unmaintainable single module

## Consequences

- (+) `nest` submodule name matches the CLI command — zero vocabulary mismatch
- (+) Cache logic lives in `parsing/` — one module owns feature file reading end-to-end
- (+) Six modules keeps the import graph shallow and testable
- (-) `parsing/` has slightly broader responsibility (parse + cache); internal structure must enforce the boundary (e.g. `parsing/cache.py` as a sub-file)
- (-) Module dependency graph updated: `Cache` context is now part of `Parsing` context
