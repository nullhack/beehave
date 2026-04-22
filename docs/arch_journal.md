# Architecture Journal: beehave

> Append-only record of all architecture design session Q&A.
> Written by the system-architect. Read by the system-architect for resume checks and ADR regeneration.
> Never edit past entries — append new session blocks only.
> If ADRs need to be regenerated, this file is the source of truth.

---

## 2026-04-22 — Session 1
Status: IN-PROGRESS

### Context

First architecture design session for beehave v1.
Covers all key architectural decisions before any implementation begins.
Resolves the 4 unanswered architectural gaps (A1–A4) from scope_journal.md Session 1.

### Gaps

| ID | Question | Answer |
|----|----------|--------|
| A1 | Error handling: How should beehave behave when pyproject.toml is malformed, a .feature file has invalid Gherkin, or the filesystem is read-only? | Malformed pyproject.toml (present but invalid) → error. Absent pyproject.toml → use defaults, no error. Invalid Gherkin → error. Read-only filesystem → error with clear message. Deleted feature file → configurable: warn (default) or error. Duplicate @id → hard error always (not configurable; see D3/D6). |
| A2 | Performance constraints: What is the target scale? This determines whether the cache is load-bearing or an optimisation. | Medium (100–1,000 Examples). Full scan acceptable. Cache is a nice-to-have speedup, not load-bearing. |
| A3 | Backwards compatibility: What is the policy for CLI flags, config keys, and @id format changes? | Best-effort: deprecation warning in one minor release before removal. No hard semver guarantee. |
| A4 | Logging and observability: Beyond --verbose and --json, should beehave support structured logging, log levels, or log files? | Standard Python logging module with log levels (DEBUG/INFO/WARN/ERROR); users can set level via config or flag. |

### Decisions

| ID | Question | Answer |
|----|----------|--------|
| D1 | Module structure: How should the beehave package be organized into submodules? | 6 submodules: cli, config, parsing, sync, adapters, nest. Cache merged into parsing (no independent public API). "scaffold" rejected — violates bee branding; renamed to "nest" to match the CLI command. |
| D2 | Adapter contract: Should FrameworkAdapter be a typing.Protocol or an ABC? | typing.Protocol. Zero import coupling for third-party adapters; pyright enforces statically. |
| D3 | @id format and stability: What is the format for @id tags and how are collisions handled? Edited/deleted @id — treat as orphan (warn or error per policy). | 8-char lowercase hex. Once assigned, never replaced unless malformed (empty or non-hex). Generation collisions trigger silent retry. Uniqueness is project-wide. Edited/deleted @id → old stub becomes orphan, subject to on_orphan policy. Duplicate @id found in files → hard error always (beehave cannot determine which stub to bind). |
| D4 | Slug derivation: How is the feature slug derived, and does the stage folder (backlog/in-progress/completed) affect it? | Slug derived from file stem only. Stage folder is ignored. Moving a feature between stage folders has zero effect on test stubs. Feature rename: no feature-level ID exists, so beehave cannot detect renames — old test directory becomes an orphan (warn or error per configured policy); new stubs generated under new slug. |
| D5 | Feature file write policy: What may beehave write to .feature files? Write strategy: surgical insertion or full reserialize? | Only @id tags on untagged Examples. All other content is read-only. Strategy: surgical line insertion (insert @id tag line above the Example: line; never reserialize the whole file). |
| D6 | Error vs. warn policy: Which conditions are always errors and which are configurable? | Always error: malformed pyproject.toml (present but invalid), invalid Gherkin syntax, read-only filesystem, duplicate @id found in any file (hard error — beehave cannot bind stub name). Configurable warn/error (default warn): deleted .feature file, orphan stub. Absent pyproject.toml is NOT an error — use defaults. Duplicate @id is never produced by beehave; if found it was hand-edited — hard error. |

### ADRs Produced This Session

| ADR | Question ID | Status |
|-----|-------------|--------|
| ADR-2026-04-22-performance-targets | A2 | Written |
| ADR-2026-04-22-backwards-compatibility | A3 | Written |
| ADR-2026-04-22-logging-observability | A4 | Written |
| ADR-2026-04-22-module-structure | D1 | Written |
| ADR-2026-04-22-adapter-protocol | D2 | Written |
| ADR-2026-04-22-id-stability | D3 | Written |
| ADR-2026-04-22-slug-derivation | D4 | Written |
| ADR-2026-04-22-feature-file-write-policy | D5 | Written |
| ADR-2026-04-22-error-handling-policy | D6 | Written |

Status: COMPLETE
