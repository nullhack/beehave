# ADR-2026-04-23-cli-subcommand-structure

## Status

Accepted

## Context

The `nest` feature introduces `beehave nest` as the first subcommand. The current `__main__.py` uses `fire.Fire(main)` which exposes a single `main` function. Adding `nest` as a subcommand requires restructuring the CLI entry point. Future commands (`sync`, `status`, `hatch`) will follow the same pattern.

## Interview

| Question | Answer |
|---|---|
| How should `beehave nest` be exposed as a CLI subcommand? | Refactor `__main__.py` to use a `BeehaveCLI` class with methods for each command, exposed via `fire.Fire(BeehaveCLI)` |
| What about module-level functions with `fire.Fire()`? | Rejected — exposes all module-level callables including helpers; no shared initialization; poor namespace control |
| What about `fire.Fire({"nest": nest_func})`? | Rejected — dict maintenance burden; doesn't scale to 5+ commands |
| What about argparse subparsers? | Rejected — verbose; inconsistent with existing Fire dependency; Fire handles this naturally |
| Does this change the existing `python -m pytest_beehave` behavior? | Yes — calling without a subcommand will print usage instead of logging "Ready." This is acceptable since the placeholder behavior has no production value. |

## Decision

Refactor `__main__.py` to use a `BeehaveCLI` class with methods for each command, exposed via `fire.Fire(BeehaveCLI)`.

## Reason

Python Fire naturally supports class-based subcommands. A class provides a clean namespace for all beehave commands and allows shared initialization (logging setup). This pattern scales to the full command set (`nest`, `sync`, `status`, `hatch`, `version`) without structural changes.

## Alternatives Considered

- **Module-level functions with `fire.Fire()`**: exposes all module-level callables; no shared initialization; poor namespace control
- **`fire.Fire({"nest": nest_func})`**: explicit but doesn't scale; dict maintenance burden
- **argparse subparsers**: more control but verbose; inconsistent with existing Fire dependency

## Consequences

- (+) Clean namespace: `beehave nest`, `beehave sync`, etc. map directly to class methods
- (+) Shared initialization via `__init__` (logging, config resolution)
- (+) Scales to 5+ commands without structural changes
- (+) Consistent with existing Fire dependency — no new runtime deps
- (-) Calling `python -m pytest_beehave` without a subcommand prints usage instead of "Ready." — acceptable since the placeholder has no production value
