# IN_20260510_sync_and_io — Feature File Sync, Caching & IO Strategy

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Project Founder
> **Session type:** Domain deep-dive

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | Determining how beehave reads and writes .feature files, when @id tags get added, how caching works, and how to minimize IO while keeping beehave effective. |
| Q2 | What is the core design principle? | Separate read and write paths. `pytest collection` is read-only — it validates and reports. `beehave sync` is the write path — it modifies .feature files. pytest never writes to source files. |

## Two-Phase Architecture

| ID | Question | Answer |
|----|----------|--------|
| Q3 | What are the two phases where beehave operates? | Phase 1: `pytest collection` (every test run) — read .feature files, validate step matching, validate @id links, validate ordering, flag orphans. Phase 2: `beehave sync` (explicit command) — add missing @id tags, report orphans, optionally generate test stubs. |
| Q4 | Why must pytest collection never write to .feature files? | Three reasons: (1) pytest is a read-only tool during collection — modifying files mid-collection is surprising behavior. (2) Writing files on every collection defeats IO minimization. (3) CI runners should not modify source files — test runs must be deterministic. |

## The @id Assignment Flow

| ID | Question | Answer |
|----|----------|--------|
| Q5 | When do scenarios get @id tags? | Only via `beehave sync`. The flow is: (1) Developer writes .feature scenario without @id. (2) Developer runs `beehave sync`. (3) beehave sync finds scenarios without @id, generates and writes IDs into the .feature file. (4) Developer can then create the test function matching the @id. (5) `pytest collection` validates — every scenario now has an @id. |
| Q6 | What happens during pytest collection if a scenario has no @id? | Flagged as a missing-id warning with a message: "run `beehave sync` to assign missing IDs." The scenario cannot be matched to any test function and cannot be cached. It is skipped for validation purposes. |
| Q7 | Must `beehave sync` be run before tests can pass? | For adoption level 1 (no .feature file), no sync is needed. For adoption level 2+ (with .feature files), `beehave sync` should be run once after creating or modifying .feature files to assign @id tags. After that, pytest collection works. |
| Q8 | Is `beehave sync` idempotent? | Yes. Running it twice does not change already-tagged scenarios. It only assigns @id tags to scenarios that lack them. |

## Caching Strategy

| ID | Question | Answer |
|----|----------|--------|
| Q9 | What caching approach does beehave use? | Option A: Parse and cache. First collection parses all .feature files, builds a dict keyed by `@id → scenario_data`, and caches to `.beehave_cache/`. Subsequent collections check file mtime and re-parse only changed files. |
| Q10 | Why not parse every time (Option B) or pre-compile to Python (Option C)? | Option B (parse every time) is simpler but re-parses all .feature files on every pytest invocation. For large projects with many .feature files, this adds unnecessary IO. Option C (pre-compile to Python) is faster but requires a build step before tests and introduces stale-data risk. Option A balances performance and simplicity — mtime checks are cheap, and caching avoids re-parsing unchanged files. |
| Q11 | What is the cache format? | `{ @id → { scenario_data, file_path, mtime } }` keyed by @id. Each entry contains the parsed scenario data, the source file path, and the file's mtime for invalidation checks. |
| Q12 | Should `.beehave_cache/` be gitignored? | Yes. It is derived data (like `__pycache__` or `.pytest_cache`) and should not be committed to version control. |
| Q13 | What about scenarios without @id? | Scenarios without @id cannot be cached — they are incomplete. They are reported as warnings during pytest collection. After `beehave sync` adds the @id, they become cacheable on the next collection. |

## Orphan Handling

| ID | Question | Answer |
|----|----------|--------|
| Q14 | How are orphan tests handled? | A Python test function with an @id suffix that has no matching .feature scenario is flagged as an orphan test. Default behavior: warning. Configurable to error via `pyproject.toml` (`strict = true`). |
| Q15 | How are orphan scenarios handled? | A .feature scenario with an @id that has no matching Python test function is flagged as an orphan scenario. Default behavior: warning. Configurable to error via `pyproject.toml` (`strict = true`). |
| Q16 | Is strict mode the default? | No. The default is permissive (warnings). `strict = true` in `pyproject.toml` upgrades warnings to errors, suitable for CI. |
| Q17 | When does orphan detection activate? | At adoption level 1 (no .feature file), orphan detection is off. At level 2+ (with .feature files), it activates. |

## The `beehave sync` Command

| ID | Question | Answer |
|----|----------|--------|
| Q18 | What does `beehave sync` do? | (1) Parse all .feature files. (2) Find scenarios without @id → generate and write IDs into the .feature files. (3) Find scenarios without matching test functions → report as orphans. (4) Find test functions without matching scenarios → report as orphans. |
| Q19 | What about `beehave sync --stubs`? | Deferred — test stub generation (creating `<rule_name>_test.py` skeleton files) will be discussed later. |
| Q20 | Should `beehave sync` detect stale @id references? | Deferred — whether sync should detect scenarios whose text changed enough that the @id no longer matches the test. Discussed later. |

## IO Minimization Summary

| ID | Question | Answer |
|----|----------|--------|
| Q21 | How does beehave minimize IO during pytest collection? | (1) Cache parsed .feature data to `.beehave_cache/`. (2) On subsequent collections, check mtime and re-parse only changed files. (3) Key cache by @id for O(1) lookup during validation. (4) Scenarios without @id are skipped (not cached, not validated). (5) pytest collection is read-only — no writes to .feature files. |
| Q22 | How does beehave minimize IO during sync? | `beehave sync` reads all .feature files and writes only to files where @id tags were missing (or where other modifications are needed). It does not rewrite unchanged files. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Performance | When pytest collects tests, .feature file parsing must not dominate collection time | After first parse, subsequent collections should only re-parse changed files (mtime check) | Must |
| QA2 | Safety | When pytest collects tests, no source files are modified | pytest collection must never write to .feature files or test files | Must |
| QA3 | Idempotency | When `beehave sync` is run multiple times, it does not modify already-tagged scenarios | Running sync twice produces the same .feature files as running once | Must |
| QA4 | Discoverability | When a scenario lacks an @id, the developer must be told what to do | Missing-id warnings must include the instruction "run `beehave sync` to assign missing IDs" | Must |

---

## Pain Points Identified

- Without a sync command, developers would have to manually assign and manage @id tags — error-prone and tedious
- If pytest collection wrote to .feature files, CI runs would be non-deterministic and could corrupt source files
- Scenarios without @id create a chicken-and-egg problem for caching and validation — sync resolves this

## Business Goals Identified

- Keep pytest collection fast and read-only — no source file modifications during test runs
- Provide `beehave sync` as the single write path for .feature file maintenance
- Make @id assignment automatic and idempotent — developers run sync and move on
- Default to warnings (permissive) so adoption is gradual; strict mode available for CI

## Terms to Define (for glossary)

- **`beehave sync`** — The explicit command that writes @id tags into .feature files and reports orphans. The only way to add or modify @id tags. Idempotent — running twice produces the same result as running once.
- **`.beehave_cache/`** — Cache directory for parsed .feature data, keyed by @id. Contains scenario data, file paths, and mtimes. Gitignored (derived data). Re-parsed only when source .feature files change (mtime check).
- **Orphan test** — A Python test function whose @id suffix has no matching .feature scenario. Warned by default, error in strict mode.
- **Orphan scenario** — A .feature scenario whose @id has no matching Python test function. Warned by default, error in strict mode.
- **Strict mode** — `pyproject.toml` configuration (`strict = true`) that upgrades warnings to errors. Suitable for CI. Default is permissive (warnings only).
- **Missing-id warning** — A warning emitted during pytest collection when a .feature scenario has no @id tag. Includes the instruction to run `beehave sync`.

## Updates to Previous INs

### IN_20260510_collection_mechanics

- **Q6** (ID generation): Updated — IDs are assigned by `beehave sync`, not during pytest collection. pytest collection is read-only.
- **Q17** (orphan detection): Updated — orphan detection uses permissive mode (warnings) by default, configurable to strict (errors) via `pyproject.toml`.
- **D2** (@example auto-generation): Deferred to the test stubs discussion.
- **D7** (Hypothesis settings tags): Confirmed — settings in `pyproject.toml`, not .feature files.

### IN_20260510_settings_and_defaults

- **Q13** (configuration location): Updated — `pyproject.toml` also includes `strict` setting (default `false`) for orphan/missing-id handling.

## Action Items

- [ ] Design the `beehave sync` command interface and output format
- [ ] Design the `.beehave_cache/` format and invalidation logic
- [ ] Decide on test stub generation (`beehave sync --stubs`) — deferred to future discussion
- [ ] Decide on stale @id detection in `beehave sync` — deferred to future discussion
- [ ] Define the `pyproject.toml` schema including `strict` setting