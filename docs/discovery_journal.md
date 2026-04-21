# Discovery Journal: beehave

---

## 2026-04-21 — Session 1
Status: COMPLETE

### General
Status: COMPLETE

| ID | Question | Answer |
|----|----------|--------|
| Q1 | Who are the users? | Developers, testers and managers that use BDD as part of their development cycle. The tool should be extensible to other test frameworks (framework-agnostic), installable via extras like `pip install beehave[pytest]`, `pip install beehave[unittest]`, etc. Wrappers (e.g. `pytest-beehave`) can be developed on each framework for deeper integration, but that level of integration is out of scope. |
| Q2 | What does the product do at a high level? | Beehave keeps the living documentation reasonably up to date. It does not check implementation specifics or change test bodies. It flags, changes, and updates whatever is mandatory, following the mantra that `.feature` files are the source of truth and `tests/` should reflect that. |
| Q3 | Why does it exist — what problem does it solve? | It is too complicated to keep living documentation and code/tests in sync. Beehave tries to make that gap smaller. |
| Q4 | When and where is it used? | It can be used as a package, and it should also have CLI capabilities. Python API: `from beehave import ...`; CLI: `beehave --<keywords>` from bash. |
| Q5 | Success — what does "done" look like? | Success is when stubs are generated and updated without destroying anything, and when the tool successfully informs the user when something changed that is beyond the scope of the project to handle. |
| Q6 | Failure — what must never happen? | Failure is when it breaks the user tests or fails to inform the user about something. Users must still be able to force changes and see dry-run changes. |
| Q7 | Out-of-scope — what are we explicitly not building? | - Not doing any coding (i.e. not modifying test implementation bodies).<br>- There is a configurable structure for tests, and that structure will be followed.<br>- Parameters should be handled the way each target framework treats them natively.<br>- Outlines should show completely in docstrings/templates per framework. |
| Q8 | What is the public API surface — CLI, Python API, or both? What is the difference between bootstrap and generate commands? | - Both CLI and Python API are first-class surfaces.<br>- CLI commands have a subtle bee-world-related flavor.<br>- Commands selected: `beehave sync`, `beehave status`, `beehave version`, `beehave nest`, `beehave hatch`.<br>- Flags: `--overwrite`.<br>- `nest`/`init` = project directory setup; `hatch`/`example` = demo content generation. |
| Q9 | How do consumers (like pytest-beehave) register marker templates? | Stubs and changes will be templated per framework adapter. Start with pytest only, then add unittest. The difference between adapters is mostly marker style and framework conventions. |
| Q10 | Who configures beehave — end developers or framework authors? | End developers. Framework authors can use it if they want to integrate, but that is not the primary concern. |
| Q11 | What is the exact relationship between `beehave` and the future `pytest-beehave` wrapper? | `pytest-beehave` is a pytest-only wrapper using `beehave` under the hood. It adds specific pytest capabilities like automatic running, HTML acceptance criteria injection, and terminal acceptance criteria. |

### Cross-cutting
Status: COMPLETE

| ID | Question | Answer |
|----|----------|--------|
| C1 | Framework detection: How does beehave know which test framework a project uses? | No auto-detect. Explicit `--framework <name>` flag (defaults to `pytest`). |
| C2 | When does beehave run? | On-demand only (developer runs CLI when they want). No watch mode, no pre-commit hooks, no auto-triggers. |
| C3 | Configuration source: Where does beehave read its configuration from? | `pyproject.toml` under `[tool.beehave]`. |
| C4 | Feature file mutability: Are `.feature` files strictly read-only source of truth for beehave? | Beehave writes to `.feature` files ONLY to add `@id` tags to Examples that have no ID. Nothing else is modified. |
| C5 | Deletion handling: What happens when a `.feature` file is deleted? | Warn by default when a `.feature` file is deleted. Configurable in `pyproject.toml` to raise an error instead. |
| C6 | Multi-framework projects: Can a single project use multiple test frameworks simultaneously? | One framework per invocation (`--framework <name>`). Generated stubs are for that framework only. Only generates stubs for Examples without a corresponding existing test (identified by `@id` in test function name). |
| C7 | Template customization: Can end users override or customize the templates that adapters use to generate stubs? | Yes — users can point to a custom template folder. |
| C8 | CLI output style: What should the terminal output look like? | Silent by default (Unix philosophy). `--verbose` for human-readable output. `--json` for machine-readable output (CI integration). |
| C9 | Test stub ownership: When beehave updates a test stub file, how does it avoid overwriting developer-written code? | Features map from source folder (`docs/features/` by default, configurable) to `tests/features/<feature_snake_name>/`. Each test function carries the `@id` in its name (`test_<feature_slug>_<id>`), making identification unambiguous. **CORRECTION (2026-04-21):** Feature files can live in four locations — `docs/features/backlog/<name>.feature`, `docs/features/in-progress/<name>.feature`, `docs/features/completed/<name>.feature`, and `docs/features/<name>.feature` (root-level, no subfolder). All four map identically to the same `tests/features/<feature_snake_name>/` directory. The stage subfolder is irrelevant to test stub mapping. |
| C10 | Feature stages (backlog/in-progress/completed): Does beehave handle these three directories differently? | No behavioral difference. After `beehave nest`, all three folders (`backlog/`, `in-progress/`, `completed/`) exist but features in any of them map identically to `tests/features/<feature_snake_name>/`. Root-level `.feature` files (no subfolder) also map identically. The structure is independent of which folder the `.feature` file lives in. |

### Architectural Cross-cutting (Gaps)
Status: RECORDED FOR FUTURE SESSION

The following questions were identified during quality review as missing architectural probes. They will be addressed in a future discovery session before v1 ships:

| ID | Question | Status |
|----|----------|--------|
| A1 | Error handling patterns: How should beehave behave when `pyproject.toml` is malformed, a `.feature` file has invalid Gherkin syntax, or the filesystem is read-only? | Unanswered |
| A2 | Performance constraints: What is the target sync time for a project with 100 / 1,000 / 10,000 Examples? Is there a memory budget? | Unanswered |
| A3 | Versioning and backwards compatibility: Will `beehave` v1 `.feature` files with `@id` tags remain compatible with v2? What is the deprecation policy for CLI flags and config keys? | Unanswered |
| A4 | Logging and observability: Beyond `--verbose`, should beehave support structured logging, log levels, or log files? | Unanswered |

### Per-feature
Status: COMPLETE

#### Feature: `nest` — bootstrap canonical directory structure

| ID | Question | Answer |
|----|----------|--------|
| N1 | What does `beehave nest` create? | Creates: `docs/features/{backlog,in-progress,completed}/`, `tests/features/`, and `.gitkeep` files in each empty directory. Also injects a `[tool.beehave]` snippet into `pyproject.toml` if not already present. |
| N2 | Who is the expected user running `nest`? | Developers setting up a new project. It is run once per repo and the result is committed. It is not intended to be run repeatedly by every contributor. |
| N3 | Partial structure? | Additive and idempotent. Creates only the missing parts; never removes or overwrites existing content. |
| N4 | pyproject.toml injection? | Yes — injects `[tool.beehave]` snippet if not present. |
| N5 | Non-default layout? | Accepts `--features-dir` argument (at minimum) to override the default `docs/features/` path. |
| N6 | Exact list of paths on green-field? | `docs/features/`, `docs/features/backlog/`, `docs/features/in-progress/`, `docs/features/completed/`, `tests/features/` — each with a `.gitkeep`. A project is considered "already nested" if `docs/features/` contains any `.feature` file; idempotency applies from that point. |
| N7 | Run twice? | Idempotent. If the project is already fully nested, warns (or errors, configurable — same pattern as C5). |
| N8 | Starter .feature file? | No — generating starter `.feature` content is strictly `hatch`'s responsibility. |
| N9 | --check mode for CI? | Yes — `nest --check` verifies the structure without modifying anything. Exits non-zero if structure is incomplete. |
| N10 | Unrelated files in directory? | Only creates what is missing. Never refuses or prompts due to unrelated files. Safe to run in an existing Python project. |
| N11 | --overwrite flag? | Yes — `nest --overwrite` recreates the structure from scratch (removes and recreates managed dirs). |

#### Feature: `id-generation` — assign @id tags to untagged Examples

| ID | Question | Answer |
|----|----------|--------|
| I1 | ID format, developer-supplied IDs, and idempotency? | - **Format:** 8-char lowercase hex when beehave generates (e.g. `@id:a1b2c3d4`).<br>- **Developer-supplied:** If a developer already added `@id:<value>`, beehave respects it as-is and never overwrites or regenerates it.<br>- **Idempotency:** Valid existing IDs are left untouched.<br>- **Malformed tags:** `@id:` with no value, or `@id:ZZZZZZZZ` (non-hex), are treated as missing — a new ID is generated and replaces the malformed one. |
| I2 | Uniqueness scope? | Project-wide (all `.feature` files). If a duplicate `@id` is detected, warn/error (configurable, same pattern as C5). |
| I3 | Collision on generation? | Retry with new random value silently until unique. |
| I4 | Write-back strategy? | In-place. Preserves all whitespace and formatting exactly — only adds the `@id:` tag line. |
| I5 | Dry-run / preview mode? | Covered by `beehave status` — no separate preview mode for id-generation. |
| I6 | Ordering? | Top-to-bottom file order. Order is not reproducible (random hex each run), but the same Example never gets a new ID once assigned. |
| I7 | Python API? | Yes — programmatic entry point available (e.g. `from beehave import assign_ids`). |

#### Feature: `status` — dry-run preview of sync changes

| ID | Question | Answer |
|----|----------|--------|
| S1 | Output and format? | - **Content:** Summary of changed files (what would change if `sync` were run), or "OK" if nothing is out of sync.<br>- **Exit codes:** Exit 0 if in sync. Exit 1 if changes are pending. Standard Unix CI contract.<br>- **Format:** Silent by default, `--verbose` for human-readable detail, `--json` for machine-readable. |

#### Feature: `cache-management` — incremental sync cache

| ID | Question | Answer |
|----|----------|--------|
| CA1 | Cache location and format? | JSON cache file at `.beehave_cache/features.json`. |
| CA2 | Cache lifecycle? | Auto-rebuilds silently if stale, missing, or corrupted. Entry added to `.gitignore` by `beehave nest`. Cache is not user-visible in normal operation. |

#### Feature: `template-customization` — user-defined stub templates

| ID | Question | Answer |
|----|----------|--------|
| T1 | Default templates? | Built-in adapter templates are the default (baked into the project). |
| T2 | Override mechanism? | User overrides by pointing to a custom template folder via `--template-dir` flag or `[tool.beehave]` config key `template_path`. |
| T3 | Override scope? | Custom template folder is a full replacement — it overrides the built-in entirely for the matched template files. |

#### Feature: `sync-create` — generate new test stubs

| ID | Question | Answer |
|----|----------|--------|
| SC1 | Generated stub structure? | Function named `test_<feature_slug>_<id>` (e.g. `test_login_a1b2c3d4`); skip marker from adapter template (not hard-coded — each adapter supplies its own skip syntax); docstring = full Gherkin scenario text (Given/When/Then steps verbatim); `-> None` return type annotation; body = `...` (Ellipsis, not `pass`). |
| SC2 | File layout? | One test file per `Rule:` block: `tests/features/<feature_snake>/<rule_slug>_test.py`. |
| SC3 | Markers? | Markers come from the adapter template (not hard-coded in core). |

#### Feature: `sync-update` — update existing test stubs

| ID | Question | Answer |
|----|----------|--------|
| SU1 | What gets updated when an Example changes? | Docstring (re-rendered to match new Gherkin steps); function name (if the feature slug changed due to file rename); `@deprecated` marker (added or removed based on Gherkin `@deprecated` tag). |
| SU2 | What about Scenario Outline column changes? | Parameters/signature for Scenario Outlines: WARN only, do not touch. Flag as "manual intervention required." |
| SU3 | Test body? | Beehave NEVER modifies the test body. |

#### Feature: `sync-cleanup` — handle orphaned test stubs

| ID | Question | Answer |
|----|----------|--------|
| SCL1 | Orphan trigger? | `@id` in test function name has no matching `@id` in any `.feature` file. |
| SCL2 | Orphan action? | Warn only — print a warning but leave the stub completely unchanged. Developer deletes manually. |
| SCL3 | Feature renamed (slug changed, IDs still match)? | Rename the test function to match new slug. Body preserved. This is sync-update territory, not cleanup. |
| SCL4 | Feature file deleted? | Warn only (C5 behavior). Test stubs become orphans — handled by orphan detection above. |
| SCL5 | Test in wrong location (IDs match but path is wrong)? | Move the test function/file to the correct location, preserving body. |

#### Feature: `adapter-contract` — common framework adapter interface

| ID | Question | Answer |
|----|----------|--------|
| AC1 | Registration mechanism? | Adapters registered via `framework = 'pytest'` (or `framework = 'unittest'`) in `[tool.beehave]` config. `--framework <name>` CLI flag overrides config. Default is `pytest` if neither is set. |
| AC2 | v1 scope? | Built-in adapters only (`pytest`). `unittest` adapter is parked for v2. |
| AC3 | What does each adapter provide? | Skip marker template, deprecated marker template, parametrize template, stub file header. |

#### Feature: `pytest-adapter` — generate pytest test stubs

| ID | Question | Answer |
|----|----------|--------|
| PA1 | Skip marker? | `@pytest.mark.skip(reason="not yet implemented")` |
| PA2 | Deprecated marker? | `@pytest.mark.deprecated` |
| PA3 | Parametrize? | `@pytest.mark.parametrize(...)` — adapter renders this from Scenario Outline columns. |
| PA4 | Function prefix? | `test_` |
| PA5 | Return type? | `-> None` |
| PA6 | Body? | `...` (Ellipsis) |

#### Feature: `parameter-handling` — Scenario Outline parametrization

| ID | Question | Answer |
|----|----------|--------|
| PH1 | Scenario Outline handling? | Adapter renders a parametrized stub using the adapter's parametrize template. |
| PH2 | Column changes after initial stub creation? | Warn only, flag as "manual intervention required." Beehave does NOT update the parametrize decorator. Developer must update manually. |

#### Feature: `unittest-adapter` — generate unittest test stubs

| ID | Question | Answer |
|----|----------|--------|
| UA1 | v1 scope? | PARKED — out of v1 scope. Moved to a separate backlog item for future work. |

#### Feature: `hatch` — generate example/demo feature files

*Baselined as-is. No per-feature questions required — behavior is fully defined by cross-cutting decisions (Q8 command palette, Q7 out-of-scope) and the supplement entry. Generating demo `.feature` files is a content concern, not a behavioral one.*

#### Feature: `config-reading` — read [tool.beehave] from pyproject.toml

*Baselined as-is. No per-feature questions required — behavior is fully defined by cross-cutting decision C3 (config source) and the feature description. Reading TOML and applying defaults is a mechanical concern with no stakeholder-facing ambiguity.*

#### Feature: `deprecation-sync` — propagate @deprecated tags to stubs

*Baselined as-is. No per-feature questions required — behavior is fully defined by cross-cutting decision C4 (feature file mutability) and the supplement correction (absolute cascade, no override). Propagation logic is deterministic and requires no further stakeholder input.*

---

## 2026-04-21 — Session 1 (Supplement)
Status: COMPLETE

### Corrections and Clarifications

| Feature | Question | Answer |
|---------|----------|--------|
| `deprecation-sync` | Does `@deprecated` cascade from Feature/Rule to child Examples? | Yes — cascade is absolute. A `@deprecated` tag on a Feature or Rule applies to all Examples beneath it. There is NO override mechanism in v1. |
| `hatch` | What should generated demo content look like? | One or two bee-themed `.feature` files covering common Gherkin patterns (Feature, Rule, Example, Scenario Outline). Enough to demo the full sync workflow end-to-end. |
