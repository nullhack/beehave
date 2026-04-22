# ADR: Backwards compatibility policy

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | all |
| **Status** | Accepted |

## Decision

beehave follows a **best-effort deprecation** policy: any CLI flag, config key, or `@id` format change is preceded by a deprecation warning visible to users for at least one minor release before removal. No hard semver guarantee is enforced.

## Reason

Stakeholder confirmed best-effort as the right balance. A hard semver contract requires versioning infrastructure (deprecation tracking, migration tooling) that is out of scope for v1. Warn-before-remove protects users without the overhead of strict semver governance.

## Alternatives Considered

- **Strict semver (breaking changes on major bumps only)**: rejected — adds governance overhead; semver tooling not yet in place for v1
- **No guarantee (v1 is pre-stable)**: rejected — even in early releases, users depend on `@id` tags being stable; silently breaking them damages trust
- **Migration tooling (automated rename/migrate on upgrade)**: deferred to v2 if needed; warn-before-remove is sufficient for v1

## Consequences

- (+) Users are never surprised by silent breakage — at least one release cycle of warning
- (+) No versioning infrastructure required in v1
- (+) `@id` tags in `.feature` files are implicitly stable (removing them would require changing all test function names — always a deprecation-warranted change)
- (-) No formal tracking mechanism for "deprecated in vX.Y" — relies on changelog discipline
- (-) Gap A3 is resolved: backwards compat is best-effort warn-before-remove; no migration tooling in v1
