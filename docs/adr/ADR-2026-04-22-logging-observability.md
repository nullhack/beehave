# ADR: Logging and observability

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | all (CLI) |
| **Status** | Accepted |

## Context

**Question (A4):** Beyond `--verbose` and `--json`, should beehave support structured logging, log levels, or log files?

Stakeholder confirmed log levels (DEBUG/INFO/WARNING/ERROR) are needed so users can control verbosity without code changes. Standard Python `logging` was the clear choice: zero extra dependency, universally understood, integrates cleanly with library use. `--verbose` maps to INFO; `--json` switches output format but respects the active level.

---

## Decision

beehave uses the **standard Python `logging` module** with four levels: DEBUG, INFO, WARNING, ERROR. The active log level is configurable via a `[tool.beehave]` key (`log_level`) or a `--log-level` CLI flag. Default level is WARNING (silent for normal use). `--verbose` is sugar for INFO; `--json` switches output format but respects the active log level.

## Reason

Stakeholder confirmed log levels (DEBUG/INFO/WARN/ERROR) are needed. The standard `logging` module is zero-dependency, universally understood, and integrates cleanly with Python tooling. Users who embed beehave as a library get standard log handler plumbing for free.

## Alternatives Considered

- **stdout/stderr only (no logging module)**: rejected — stakeholder wants level control; adding it later would be a breaking change to output contracts
- **structlog / loguru**: rejected — third-party dependency not justified for v1; standard `logging` is sufficient
- **Log file output**: deferred — not requested; can be added via standard logging `FileHandler` in v2 without any API changes

## Consequences

- (+) Users can silence beehave completely (WARNING default) or enable diagnostics (DEBUG) without code changes
- (+) Library consumers can attach their own log handlers
- (+) `--verbose` and `--json` remain valid shortcuts; they map to level INFO
- (-) `--verbose` and `--json` are now slightly redundant with `--log-level INFO`; documented as convenience aliases
- (-) Log level must be parsed early (before config file read) to capture config-parsing diagnostics
- (-) Gap A4 is resolved: standard Python logging, four levels, config key + CLI flag, default WARNING
