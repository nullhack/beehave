# ADR-2026-04-23-nest-module-placement

## Status

Accepted

## Context

The `nest` feature requires directory creation, pyproject.toml injection, .gitignore updates, check mode, and overwrite mode. The existing `bootstrap.py` module already handles canonical subfolder creation and loose feature file migration, but it does not cover pyproject.toml, .gitignore, check mode, or overwrite mode. The nest command is a distinct CLI use case that orchestrates multiple concerns beyond directory bootstrapping.

## Interview

| Question | Answer |
|---|---|
| Should the nest logic extend `bootstrap.py` or live in a new module? | New `nest.py` module — nest is a use case that delegates to bootstrap for directory concerns but adds config injection, gitignore, check, and overwrite |
| Can `nest.py` reuse `_ensure_canonical_subfolders` from `bootstrap.py`? | No — that function only creates subfolders under an existing root; nest needs to create the root itself, plus `tests/features/`, plus `.gitkeep` files. The overlap is minimal; duplicating the subfolder constant is simpler than importing a private function. |
| What about the `BootstrapResult` type? | `NestResult` is a separate value object — it carries different fields (pyproject_modified, gitignore_modified, missing) that don't apply to the bootstrap concern. |

## Decision

Create a new `pytest_beehave/nest.py` module with its own `NestConfig`, `NestResult`, and `nest()` function. Do not extend `bootstrap.py`.

## Reason

SRP — `bootstrap.py` handles directory structure migration; `nest.py` orchestrates the full `beehave nest` workflow. The nest command is a use case that encompasses directory creation, config injection, and gitignore management. Merging these into `bootstrap.py` would violate SRP and make both concerns harder to test independently.

## Alternatives Considered

- **Extend `bootstrap.py`**: mixes directory creation with config injection and gitignore concerns; violates SRP
- **Put everything in `__main__.py`**: puts business logic in the CLI layer; violates separation of concerns

## Consequences

- (+) Each module has a single responsibility; testable in isolation
- (+) `bootstrap.py` remains unchanged — no risk of regressions in existing tests
- (+) `nest.py` can evolve independently as the nest command grows
- (-) The canonical subfolder names (`backlog`, `in-progress`, `completed`) are defined in both `bootstrap.py` and `nest.py` — acceptable since they are stable domain constants, not logic
