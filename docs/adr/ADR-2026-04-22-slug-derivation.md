# ADR: Slug derivation is stage-folder-independent

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | sync-create, sync-update, sync-cleanup, nest |
| **Status** | Accepted |

## Decision

`FeatureSlug` is derived solely from the `.feature` file's **stem** (filename without extension and without the stage subfolder path); the stage folder (`backlog/`, `in-progress/`, `completed/`, or root) is ignored.

## Reason

A feature moves through stage folders during its lifecycle. If the slug included the stage path, moving a feature from `in-progress/` to `completed/` would change the slug, rename the test directory, and orphan all stubs — a destructive side-effect of a purely administrative operation.

## Alternatives Considered

- **Include stage folder in slug**: rejected — causes spurious orphans and renames on every stage transition
- **Flat features directory (no stage subfolders)**: rejected — the stage folder structure is a project requirement (from `nest` feature)
- **Configurable slug derivation**: rejected — YAGNI; one derivation rule is sufficient for v1

## Consequences

- (+) Moving a feature between stage folders has zero effect on test stubs
- (+) Slug derivation is a pure function of the file stem — simple and testable
- (-) Two feature files with the same stem in different stage folders would collide (e.g. `backlog/login.feature` and `in-progress/login.feature`). This is treated as a user error — beehave warns and uses the first one found. The WIP-limit-of-1 workflow enforced by AGENTS.md makes this practically impossible.
