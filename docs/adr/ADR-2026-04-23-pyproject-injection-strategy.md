# ADR-2026-04-23-pyproject-injection-strategy

## Status

Accepted

## Context

The `nest` feature must inject a `[tool.beehave]` section into `pyproject.toml` if it is not already present. The existing `config.py` module already reads from `[tool.beehave]` via `_read_beehave_section`. The injection is a write operation that complements the existing read operations. The question is where to place the injection logic and how to handle the TOML write-back safely.

## Interview

| Question | Answer |
|---|---|
| Where should the injection logic live? | In `config.py` — it already owns `[tool.beehave]` reading; adding the write keeps pyproject.toml I/O cohesive |
| Should injection use `tomllib` + manual write-back or a TOML write library? | `tomllib` + string append — `tomllib` is read-only (stdlib), but the injection only appends a section at the end of the file. Full TOML round-tripping is unnecessary for appending a new section. |
| What if `[tool.beehave]` already exists? | No-op — return False. The nest command is idempotent. |
| What if `[tool]` exists but `[tool.beehave]` does not? | Append `[tool.beehave]` after the existing `[tool.*]` sections. Simple string append with a newline separator is sufficient. |
| Should we use a TOML write library like `tomlkit`? | No — adds a runtime dependency for a single append operation. YAGNI. |

## Decision

Add `inject_beehave_section()` to `config.py`. Use `tomllib` to check if the section exists, then append the snippet as a string if absent.

## Reason

Keeping the injection in `config.py` maintains cohesion — all `[tool.beehave]` I/O lives in one module. String append is sufficient because injection only adds a new section at the end of the file; it never modifies existing content. Adding a TOML write library for a single append operation violates YAGNI.

## Alternatives Considered

- **`tomlkit` for round-trip editing**: adds a runtime dependency; overkill for appending a section
- **Put injection in `nest.py`**: scatters pyproject.toml I/O across modules; `config.py` already owns this concern
- **Full TOML serialization**: unnecessary complexity for an append-only operation

## Consequences

- (+) All `[tool.beehave]` I/O in one module — easy to find and maintain
- (+) No new runtime dependencies — stdlib only
- (+) Idempotent by design — checks before writing
- (-) String append may produce non-canonical TOML formatting if the file lacks a trailing newline — mitigated by checking and adding a newline before the snippet
- (-) Does not handle the case where `[tool]` exists without `[tool.beehave]` with perfect placement — the snippet is appended at the end, which is valid TOML but not grouped with other `[tool.*]` sections. Acceptable for v1.
