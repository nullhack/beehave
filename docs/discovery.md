# Discovery: beehave

---

## Session: 2026-04-21 — Initial Synthesis (General + Cross-cutting)

### Scope
Beehave is a standalone CLI tool and Python library that keeps BDD living documentation in sync with test stubs. It treats `.feature` files as the source of truth and generates or updates test stubs in `tests/features/` without ever modifying test implementation bodies. Developers invoke it on-demand via CLI commands with subtle bee-world theming (`nest`, `hatch`, `sync`, `status`). The tool is framework-agnostic through pluggable adapters, starting with pytest. Configuration lives in `pyproject.toml` under `[tool.beehave]`. Output is silent by default (Unix philosophy), with `--verbose` and `--json` options for human and machine consumption. Beehave writes to `.feature` files only to add missing `@id` tags; all other mutations happen in `tests/`.

### Feature List
| Feature | Concern | Priority |
|---------|---------|----------|
| `nest` | Bootstrap the canonical `docs/features/` directory structure with `backlog/`, `in-progress/`, and `completed/` subfolders. | Foundational |
| `hatch` | Generate bee-themed example/demo `.feature` files to showcase capabilities. | Foundational |
| `config-reading` | Read `[tool.beehave]` from `pyproject.toml`; apply defaults. | Foundational |
| `id-generation` | Detect untagged Examples, generate unique `@id` tags, and write them back to `.feature` files. | Core |
| `sync-create` | Generate new test stubs for Examples that have no corresponding test function. | Core |
| `sync-update` | Refresh auto-generated parts of existing test stubs (docstrings, markers, signatures) when the `.feature` Example changes. | Core |
| `sync-cleanup` | Detect and warn on orphan test stubs whose `.feature` file or `@id` no longer exists. | Core |
| `status` | Dry-run preview of what `sync` would do without making any changes. | Core |
| `adapter-contract` | Define the abstract interface / protocol that all framework adapters must implement. | Core |
| `pytest-adapter` | Generate pytest-specific test stubs (top-level functions, markers, docstrings, `raise NotImplementedError`). | Core |
| `unittest-adapter` | Generate unittest-specific test stubs (future; not first release). | Backlog |
| `template-customization` | Allow users to point to a custom template folder that overrides adapter defaults. | Extended |
| `cache-management` | Maintain `.beehave_cache/` for incremental sync (hash-based change detection). | Extended |
| `deprecation-sync` | Propagate `@deprecated` Gherkin tags to framework-specific deprecation markers on stubs. | Extended |
| `parameter-handling` | Generate parametrized stubs from Scenario Outlines using native framework conventions (e.g., `@pytest.mark.parametrize`). | Extended |

**Splits applied:**
- `framework-adapters` → `pytest-adapter` + `unittest-adapter` (>2 concerns).
- `sync` → `sync-create` + `sync-update` + `sync-cleanup` (>2 concerns).

### Domain Model
| Type | Name | Description |
|------|------|-------------|
| Noun | `.feature` file | Gherkin source-of-truth file containing Feature, Rule, and Example blocks |
| Noun | feature slug | `.feature` file stem with hyphens → underscores, lowercase |
| Noun | rule slug | `Rule:` title slugified with underscores, lowercase |
| Noun | Example | Gherkin scenario (including Scenario Outline instances) |
| Noun | `@id` tag | `@id:<8-char-hex>` identifier attached to an Example |
| Noun | test stub | Auto-generated test function with docstring and `raise NotImplementedError` body |
| Noun | test directory | `tests/features/<feature_snake_name>/` mapping from source folder |
| Noun | test file | `<rule_slug>_test.py` or `examples_test.py` |
| Noun | backlog stage | `docs/features/backlog/` — organizational folder |
| Noun | in-progress stage | `docs/features/in-progress/` — organizational folder |
| Noun | completed stage | `docs/features/completed/` — organizational folder |
| Noun | orphan stub | Test function whose `@id` no longer exists in any `.feature` file |
| Noun | adapter | Framework-specific stub generator (pytest, unittest, …) |
| Noun | template | Jinja-like (or literal string) template used by an adapter to render a stub |
| Noun | `[tool.beehave]` | Configuration section in `pyproject.toml` |
| Noun | `features_path` | Configurable root path for `.feature` files (default `docs/features/`) |
| Noun | `.beehave_cache/` | Directory storing hashes for incremental sync |
| Verb | nest | Create canonical features directory and subfolders |
| Verb | hatch | Write example/demo `.feature` files to the features path |
| Verb | sync | Scan, diff, generate, update, and warn — the main orchestration command |
| Verb | status | Dry-run preview of sync operations |
| Verb | generate ID | Produce a unique 8-character lowercase hex string |
| Verb | write back | Insert `@id` tag into `.feature` file in-place |
| Verb | create stub | Write a new test function for a new Example |
| Verb | update stub | Rewrite docstring/tags of an existing test function without touching its body |
| Verb | warn orphan | Emit a warning when a `.feature` file or Example is deleted |
| Verb | deprecate stub | Apply framework-specific deprecation marker when `@deprecated` tag is present |
| Verb | parametrize | Generate framework-native parametrized stub from Scenario Outline Examples table |

### Decisions
- **No auto-detect**: Framework is explicit via `--framework <name>` (default `pytest`).
- **On-demand only**: No watch mode, no pre-commit hooks, no auto-triggers.
- **Config source**: `pyproject.toml` under `[tool.beehave]` only.
- **Feature file mutability**: Beehave writes to `.feature` files ONLY to add `@id` tags to Examples that have no ID.
- **Deletion handling**: Warn by default when a `.feature` file is deleted; configurable to error instead.
- **One framework per invocation**: `--framework` targets a single adapter per run.
- **Template customization**: Users can point to a custom template folder.
- **CLI output**: Silent by default; `--verbose` for human output; `--json` for machine-readable output.
- **Stub ownership**: `@id` in function name (`test_<feature_slug>_<id>`) makes identification unambiguous; no section comments. Feature files may live in `docs/features/backlog/`, `docs/features/in-progress/`, `docs/features/completed/`, or `docs/features/` (root-level, no subfolder) — all four locations map identically to `tests/features/<feature_snake_name>/`. The stage subfolder is irrelevant to test stub mapping.
- **Feature stages**: No behavioral difference between `backlog/`, `in-progress/`, `completed/`, or root-level — all map identically to `tests/features/<feature_snake_name>/`.

Template §3: CONFIRMED — stakeholder approved 2026-04-21

---

## Session: 2026-04-21 — Per-feature Discovery (Session 1 Complete)

### Summary

Session 1 is now fully complete. All per-feature questions were answered by the stakeholder. The following decisions were made and recorded:

**ID Generation**
- IDs are 8-char lowercase hex, generated randomly and retried silently on collision.
- Developer-supplied `@id` values are always respected; malformed tags (empty value or non-hex) are treated as missing and replaced.
- Uniqueness is project-wide across all `.feature` files.
- Write-back is in-place, preserving all whitespace and formatting.
- Idempotent: valid existing IDs are never touched.
- Python API: `from beehave import assign_ids`.
- Dry-run preview is via `beehave status` (no separate preview mode for id-generation).

**Status**
- Exit 0 = in sync; Exit 1 = changes pending. Standard Unix CI contract.
- Output: silent by default, `--verbose` for human detail, `--json` for machine-readable.
- Reports what `sync` would do without making any changes.

**Cache Management**
- Cache file: `.beehave_cache/features.json`.
- Auto-rebuilds silently if stale/missing/corrupted.
- `beehave nest` adds `.beehave_cache/` to `.gitignore`.
- Not user-visible in normal operation.

**Template Customization**
- Override via `--template-dir` CLI flag or `template_path` in `[tool.beehave]`.
- Custom folder is a full replacement for matched built-in template files.
- Built-in templates remain default when no custom folder is configured.

**Sync-Create**
- One test file per `Rule:` block: `tests/features/<feature_snake>/<rule_slug>_test.py`.
- Stub: `test_<feature_slug>_<id>`, skip marker from adapter template, verbatim Gherkin docstring, `-> None`, body `...`.
- All markers come from the adapter template (core is framework-agnostic).

**Sync-Update**
- Updates only: docstring, function name (on feature rename), `@deprecated` marker.
- NEVER modifies the test body.
- Scenario Outline column changes: WARN only, flag as "manual intervention required."

**Sync-Cleanup**
- Orphan = `@id` in test function name has no matching `@id` in any `.feature` file.
- Orphan action: warn only, leave stub unchanged.
- Feature renamed: rename test function (sync-update territory), preserve body.
- Feature deleted: warn only (C5 behavior); stubs become orphans.
- Test in wrong location: move to correct location, preserve body.

**Adapter Contract**
- Registered via `framework` key in `[tool.beehave]`; `--framework` CLI flag overrides.
- Default: `pytest`. v1 built-in adapters only.
- Each adapter provides: skip marker template, deprecated marker template, parametrize template, stub file header.

**Pytest Adapter**
- Skip: `@pytest.mark.skip(reason="not yet implemented")`
- Deprecated: `@pytest.mark.deprecated`
- Parametrize: `@pytest.mark.parametrize(...)`
- Prefix: `test_`, return type: `-> None`, body: `...`

**Parameter Handling**
- Scenario Outlines → adapter renders parametrized stub.
- Column changes after stub creation: warn only, "manual intervention required."

**Unittest Adapter**
- PARKED for v2. Out of v1 scope.

**Hatch, Config-Reading, Deprecation-Sync**
- Baselined as-is. No per-feature questions required.

### Updated Domain Model

| Type | Name | Description |
|------|------|-------------|
| Noun | `.feature` file | Gherkin source-of-truth file containing Feature, Rule, and Example blocks |
| Noun | feature slug | `.feature` file stem with hyphens → underscores, lowercase |
| Noun | rule slug | `Rule:` title slugified with underscores, lowercase |
| Noun | Example | Gherkin scenario (including Scenario Outline instances) |
| Noun | `@id` tag | `@id:<8-char-hex>` identifier attached to an Example |
| Noun | malformed `@id` | `@id:` with no value, or `@id:` with non-hex characters — treated as missing |
| Noun | test stub | Auto-generated test function with docstring and `...` body |
| Noun | test directory | `tests/features/<feature_snake_name>/` mapping from source folder |
| Noun | test file | `<rule_slug>_test.py` — one per `Rule:` block |
| Noun | orphan stub | Test function whose `@id` no longer exists in any `.feature` file |
| Noun | adapter | Framework-specific stub generator (pytest, unittest, …) |
| Noun | adapter template | Template supplied by adapter for skip, deprecated, parametrize markers, and stub header |
| Noun | template folder | Directory of template files; custom folder fully replaces built-in for matched files |
| Noun | `[tool.beehave]` | Configuration section in `pyproject.toml` |
| Noun | `features_path` | Configurable root path for `.feature` files (default `docs/features/`) |
| Noun | `framework` | Config/CLI key selecting the adapter (default `pytest`) |
| Noun | `deletion_mode` | Config key: `warn` (default) or `error` on `.feature` file deletion |
| Noun | `template_path` | Config/CLI key pointing to custom template folder |
| Noun | `.beehave_cache/` | Directory storing `features.json` hash cache for incremental sync |
| Noun | backlog stage | `docs/features/backlog/` — organizational folder |
| Noun | in-progress stage | `docs/features/in-progress/` — organizational folder |
| Noun | completed stage | `docs/features/completed/` — organizational folder |
| Verb | nest | Create canonical features directory, subfolders, `.gitignore` entry |
| Verb | hatch | Write bee-themed example/demo `.feature` files to the features path |
| Verb | sync | Scan, diff, generate, update, and warn — the main orchestration command |
| Verb | status | Dry-run preview of sync operations; exit 0/1 CI gate |
| Verb | generate ID | Produce a unique 8-character lowercase hex string, retry on collision |
| Verb | write back | Insert `@id` tag into `.feature` file in-place, preserving formatting |
| Verb | create stub | Write a new test function for a new Example |
| Verb | update stub | Rewrite docstring/tags of an existing test function without touching its body |
| Verb | warn orphan | Emit a warning when a `.feature` file or Example is deleted |
| Verb | deprecate stub | Apply framework-specific deprecation marker when `@deprecated` tag is present |
| Verb | parametrize | Generate framework-native parametrized stub from Scenario Outline Examples table |
| Verb | move stub | Relocate test function/file to correct path when location is wrong |
| Verb | assign IDs | Python API entry point: `from beehave import assign_ids` |

### Feature List (Final v1 Scope)

| Feature | One-line Description | Status |
|---------|---------------------|--------|
| `nest` | Bootstrap canonical `docs/features/` directory structure with stage subfolders | BASELINED |
| `hatch` | Generate bee-themed example/demo `.feature` files showcasing all capabilities | BASELINED |
| `config-reading` | Read `[tool.beehave]` from `pyproject.toml`; apply defaults; hard error on invalid config | BASELINED |
| `id-generation` | Detect untagged Examples, generate unique 8-char hex `@id` tags, write back in-place | BASELINED |
| `sync-create` | Generate new test stubs for Examples with no corresponding test function | BASELINED |
| `sync-update` | Refresh docstring, function name, and `@deprecated` marker when Example changes | BASELINED |
| `sync-cleanup` | Detect orphan stubs (no matching `@id`) and warn; move misplaced stubs | BASELINED |
| `status` | Dry-run preview of sync changes; exit 0/1 CI gate | BASELINED |
| `adapter-contract` | Abstract interface all framework adapters must implement | BASELINED |
| `pytest-adapter` | Default adapter: pytest markers, `test_` prefix, `-> None`, `...` body | BASELINED |
| `template-customization` | User-defined template folder overrides built-in adapter templates | BASELINED |
| `cache-management` | `.beehave_cache/features.json` for incremental sync; auto-rebuilds silently | BASELINED |
| `deprecation-sync` | Propagate `@deprecated` Gherkin tag to framework deprecation marker on stubs | BASELINED |
| `parameter-handling` | Render parametrized stubs from Scenario Outlines; warn on column changes | BASELINED |
| `unittest-adapter` | *(PARKED — v2)* unittest.TestCase stubs; out of v1 scope | PARKED |

### Open Questions
- **A1 — Error handling patterns:** How should beehave behave when `pyproject.toml` is malformed, a `.feature` file has invalid Gherkin syntax, or the filesystem is read-only?
- **A2 — Performance constraints:** What is the target sync time for projects with 100 / 1,000 / 10,000 Examples? Is there a memory budget?
- **A3 — Versioning and backwards compatibility:** Will beehave v1 `.feature` files with `@id` tags remain compatible with v2? What is the deprecation policy for CLI flags and config keys?
- **A4 — Logging and observability:** Beyond `--verbose`, should beehave support structured logging, log levels, or log files?

> These architectural gaps were identified during quality review and are scheduled for a future discovery session before v1 ships.

### Corrections (2026-04-21 Supplement)
- **`deprecation-sync`**: `@deprecated` cascade from Feature/Rule to child Examples is **absolute** — there is no override mechanism in v1. The `@deprecated-off` Example in the criteria was removed.
- **`hatch`**: Generates one or two bee-themed `.feature` files covering common Gherkin patterns (Feature, Rule, Example, Scenario Outline).
