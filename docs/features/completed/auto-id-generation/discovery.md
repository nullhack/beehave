# Discovery: auto-id-generation

## State
Status: BASELINED

## Entities
| Type | Name | Candidate Class/Method | In Scope |
|------|------|----------------------|----------|
| Noun | Example block | Gherkin scenario | Yes |
| Noun | `@id` tag | `@id:<8-char-hex>` tag on Example | Yes |
| Noun | `.feature` file | Gherkin feature file on disk | Yes |
| Noun | hex ID | 8-character lowercase hex string | Yes |
| Noun | CI environment | read-only or automated environment | Yes |
| Verb | detect missing ID | scan Example tags for `@id` | Yes |
| Verb | generate ID | produce a unique 8-char hex string | Yes |
| Verb | write back | insert `@id` tag into `.feature` file in-place | Yes |
| Verb | fail run | abort pytest with a clear error message | Yes |

## Rules
- Every `Example:` block MUST have an `@id:<8-char-hex>` tag before the stub sync proceeds
- If any Example lacks an `@id` tag AND the `.feature` file is writable, generate an ID and write it back in-place, then continue
- If any Example lacks an `@id` tag AND the `.feature` file is NOT writable (CI / read-only), fail the pytest run with a descriptive error: "Untagged Examples found — run pytest locally to generate IDs"
- Generated IDs are 8-character lowercase hexadecimal strings, unique within the feature file being processed
- IDs are written on the line immediately before the `Example:` keyword

## Constraints
- Must not corrupt the `.feature` file — only insert the `@id` tag line, leave all other content unchanged
- Must detect read-only filesystem before attempting write (check file writability, not just `CI` env var)
- The error message must name the specific `.feature` file(s) and Example title(s) that are missing IDs

## Questions
| ID | Question | Answer | Status |
|----|----------|--------|--------|
| Q1 | Should ID uniqueness be guaranteed globally (across all feature files) or just within a single file? | Within-file only — scan the current `.feature` file for existing `@id` values before generating new ones for that file; 8-char hex collision probability across files is negligible | ANSWERED (REVISED) |
| Q2 | How is "CI / read-only" detected — by checking file writability or by checking a `CI` env var? | Check file writability — more reliable across different CI systems | ANSWERED |

## Architecture

### Module Structure
- `pytest_beehave/id_generator.py` — NEW: all ID generation and write-back logic
- `pytest_beehave/plugin.py` — EXTEND: call `assign_ids` before `sync_stubs` in `pytest_sessionstart`
- `pytest_beehave/syncer.py` — unchanged (public API `sync_stubs` signature unchanged)

### Key Decisions

ADR-001: New `id_generator.py` module (not extending `syncer.py`)
Decision: Create `pytest_beehave/id_generator.py` with a single public function `assign_ids(features_dir, tests_dir=None)`.
Reason: SOLID-S — ID assignment (write `.feature` files) and stub sync (write `.py` files) are separate reasons to change; mixing them in `syncer.py` would violate SRP.
Alternatives considered: Adding `assign_ids` to `syncer.py` — rejected because it conflates two distinct file-writing concerns.

ADR-002: Writability check via `os.access(path, os.W_OK)`
Decision: Detect read-only files using `os.access(feature_path, os.W_OK)`.
Reason: Discovery constraint Q2 explicitly requires checking file writability, not the `CI` env var; `os.access` is the standard POSIX mechanism.
Alternatives considered: Checking `os.environ.get("CI")` — rejected per discovery answer; checking `stat.S_IWRITE` — lower-level, same result, less readable.

ADR-003: Collect existing IDs within the current file, then generate new unique IDs for that file
Decision: In `assign_ids`, for each `.feature` file being processed, scan only that file to collect the current `frozenset[str]` of existing `@id` values, then generate new IDs that are not already present in that same file.
Reason: Stakeholder clarified (`@id:27cf14bf`) that uniqueness is required within a single feature file only; 8-char hex collision probability across separate files is negligible and does not justify scanning all files on every run.
Alternatives considered: Scanning all `.feature` files globally — rejected per stakeholder clarification; it adds unnecessary I/O and was based on a now-deprecated requirement (`@deprecated @id:09a986e7`).

ADR-004: `assign_ids` returns `list[str]` of error descriptions for read-only files with missing IDs
Decision: `assign_ids(features_dir)` returns a list of error strings (`"<file>: Example '<title>' has no @id"`). The caller (`plugin.py`) decides whether to `pytest.exit()`.
Reason: Keeps `id_generator.py` free of pytest imports (SOLID-D); `plugin.py` already owns the `pytest.exit()` pattern.
Alternatives considered: Raising a custom exception — rejected; `pytest.exit()` is not an exception and should not be emulated by a domain module.

ADR-005: Text-based write-back (regex line insertion, not Gherkin re-serialization)
Decision: Insert `  @id:<hex>\n` on the line immediately before `  Example:` using a regex that matches the line start.
Reason: The constraint "must not corrupt the `.feature` file" is best satisfied by minimal text surgery; re-serializing via the Gherkin AST would reformat whitespace and lose comments.
Alternatives considered: AST round-trip — rejected because `gherkin-official`'s AST parser has no serializer; manual re-serialization is error-prone.

### Build Changes (needs PO approval: no)
- No new runtime dependencies (`os`, `re`, `secrets` are all stdlib)
- `id_generator.py` is a new module under the existing `pytest_beehave` package
