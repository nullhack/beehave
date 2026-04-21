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
- **Stub ownership**: `@id` in function name (`test_<feature_slug>_<id>`) makes identification unambiguous; no section comments.
- **Feature stages**: No behavioral difference between `backlog/`, `in-progress/`, and `completed/` — all map identically to `tests/features/<feature_snake_name>/`.

Template §3: CONFIRMED — stakeholder approved 2026-04-21
