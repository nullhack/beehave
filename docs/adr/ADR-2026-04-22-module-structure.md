# ADR: Package module structure — seven bounded contexts

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | all |
| **Status** | Accepted |

## Decision

The `beehave` package is organized into seven submodules matching the seven bounded contexts: `cli`, `config`, `parsing`, `sync`, `adapters`, `cache`, `scaffold`. Each submodule has a single responsibility and a strict dependency order (see domain-model.md Module Dependency Graph).

## Reason

The domain analysis reveals seven distinct responsibilities with clear boundaries. Flat module structure would mix parsing, sync, and adapter concerns, making it impossible to test them in isolation and difficult to add new adapters or cache backends later.

## Alternatives Considered

- **Flat package (all in `beehave/`)**: rejected — 14 features across 7 concerns; flat structure would produce a 1000+ line module with no clear seams
- **Three layers (core/adapters/cli)**: considered — too coarse; `parsing` and `sync` have different change rates and different external dependencies
- **Domain-driven with ports/adapters folders**: considered — over-engineered for v1; the `adapters/` submodule already provides the extension point; explicit `ports/` folder adds ceremony without benefit

## Consequences

- (+) Each submodule can be tested in isolation with no mocking of other submodules
- (+) New adapters are added by creating a new class in `beehave/adapters/` — no other module changes
- (+) `parsing` and `cache` are independently replaceable
- (-) Seven submodules means seven `__init__.py` files and more import paths to maintain
- (-) The `sync` module is the most complex (depends on parsing, adapters, cache) — it must be carefully bounded
