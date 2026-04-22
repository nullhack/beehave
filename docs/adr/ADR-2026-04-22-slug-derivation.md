# ADR: Slug derivation is stage-folder-independent

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | sync-create, sync-update, sync-cleanup, nest |
| **Status** | Accepted |

## Context

**Question (D4):** How is the feature slug derived? Does the stage folder (`backlog/`, `in-progress/`, `completed/`) affect it? What happens when a feature file is renamed?

A feature moves through stage folders during its lifecycle. If the slug included the stage path, moving from `in-progress/` to `completed/` would change the slug, rename the test directory, and orphan all stubs — a destructive side-effect of a purely administrative operation. The stakeholder confirmed stage-folder-independence. On rename: no feature-level ID exists, so beehave cannot detect renames; auto-rename was explicitly rejected (cannot distinguish rename from delete + new file).

---

## Decision

`FeatureSlug` is derived solely from the `.feature` file's **stem** (filename without extension and without the stage subfolder path); the stage folder (`backlog/`, `in-progress/`, `completed/`, or root) is ignored.

## Reason

A feature moves through stage folders during its lifecycle. If the slug included the stage path, moving a feature from `in-progress/` to `completed/` would change the slug, rename the test directory, and orphan all stubs — a destructive side-effect of a purely administrative operation.

## Feature Rename Behaviour

There is no feature-level `@id` — beehave has no way to detect that `user-login.feature` is a rename of `login.feature` rather than a brand-new feature. On rename:

- The old test directory (`tests/features/login/`) becomes a **slug orphan**: no feature maps to it
- beehave warns (or errors, per `on_orphan_feature` config) and lists the orphaned directory
- New stubs are generated under `tests/features/user_login/`
- The developer is responsible for manually migrating test bodies from the old directory to the new one

**Auto-rename was explicitly rejected** (see Alternatives).

## Alternatives Considered

- **Include stage folder in slug**: rejected — causes spurious orphans and renames on every stage transition
- **Auto-rename test directory on feature file rename**: rejected — beehave has no feature-level ID and cannot distinguish a rename from a delete + new file; auto-rename would silently corrupt test history
- **Flat features directory (no stage subfolders)**: rejected — the stage folder structure is a project requirement (from `nest` feature)
- **Configurable slug derivation**: rejected — YAGNI; one derivation rule is sufficient for v1

## Consequences

- (+) Moving a feature between stage folders has zero effect on test stubs
- (+) Slug derivation is a pure function of the file stem — simple and testable
- (+) No silent data loss — rename is always surfaced as an orphan warning/error
- (-) Feature rename requires manual test directory migration by the developer
- (-) Two feature files with the same stem in different stage folders would collide (e.g. `backlog/login.feature` and `in-progress/login.feature`). This is treated as a user error — beehave warns and uses the first one found. The WIP-limit-of-1 workflow enforced by AGENTS.md makes this practically impossible.
