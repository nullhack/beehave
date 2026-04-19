# Discovery: pytest-beehave

---

## Session: 2026-04-18 — Initial Synthesis

### Scope
pytest-beehave is a pytest plugin for Python developers using the python-project-template workflow. It eliminates the manual `gen-tests` step by automatically syncing test stubs from Gherkin `.feature` files on every `pytest` invocation — before collection, so new stubs are collected in the same run. It generates IDs for untagged Examples (failing hard in CI), writes step docstrings, and applies deprecation markers. The plugin is always-on with a configurable features folder path. It never modifies test bodies and must not corrupt `.feature` files. Out of scope: new test runner, non-standard layouts, GUI, Gherkin parser changes.

Feature stages determine what the plugin does: backlog and in-progress features receive full stub creation and updates; completed features receive only orphan detection. Marker ownership is strictly split — stub-sync owns skip/deprecated markers; the developer owns slow.

### Feature List
- `features-path-config` — custom features folder path via pyproject.toml
- `plugin-hook` — pytest lifecycle integration (register plugin, run before collection)
- `auto-id-generation` — detect missing @id tags, generate IDs, write back or fail in CI
- `stub-creation` — create new test stubs for backlog/in-progress; top-level functions, skip marker, docstrings
- `stub-updates` — update/rename/orphan-mark existing stubs; conformance enforcement; non-conforming redirect
- `deprecation-sync` — toggle @pytest.mark.deprecated across all 3 feature stages; Gherkin tag inheritance

### Domain Model
| Type | Name | Description | In Scope |
|------|------|-------------|----------|
| Noun | test stub | top-level function `test_<feature_slug>_<@id>()` | Yes |
| Noun | test file | `<rule_slug>_test.py` or `examples_test.py` | Yes |
| Noun | feature slug | `.feature` file stem, hyphens → underscores, lowercase | Yes |
| Noun | rule slug | `Rule:` title slugified with underscores, lowercase | Yes |
| Noun | docstring | verbatim step-by-step content in test stub | Yes |
| Noun | backlog stage | `docs/features/backlog/` | Yes |
| Noun | in-progress stage | `docs/features/in-progress/` | Yes |
| Noun | completed stage | `docs/features/completed/` — stub creation excluded | Yes |
| Noun | conforming test | test with correct file name AND correct function name | Yes |
| Noun | orphan test | test function with no matching `@id` in any `.feature` file | Yes |
| Verb | create stub | write new top-level test function for new Example | Yes |
| Verb | mark orphan | apply `@pytest.mark.skip(reason="orphan: ...")` | Yes |
| Verb | mark non-conforming | apply `@pytest.mark.skip(reason="non-conforming: moved to <file>")` | Yes |
| Verb | deprecate stub | apply `@pytest.mark.deprecated` when Gherkin `@deprecated` tag present | Yes |

Template §3: CONFIRMED — stakeholder approved 2026-04-18

---

## Session: 2026-04-18 — Behavior Groups

### Scope
Behavior groups and cross-cutting concerns established for the initial feature set.

### Decisions
- **Lifecycle**: backlog + in-progress receive full stub creation and updates; completed receives orphan detection only — no new stubs, no docstring/rename updates
- **Conformance**: two-part — correct file name (`<rule_slug>_test.py` or `examples_test.py`) AND correct function name (`test_<feature_slug>_<@id>`) — both must match
- **Marker ownership**: two non-overlapping domains — stub-sync owns `skip/not-yet-implemented`, `skip/orphan`, `skip/non-conforming`, `deprecated`; developer owns `slow` — neither crosses into the other's territory

---

## Session: 2026-04-18 — Per-feature scope: features-path-config, plugin-hook, deprecation-sync, auto-id-generation

### Feature List
- `features-path-config` — custom features folder path via pyproject.toml; default `docs/features/`; hard error on missing configured path
- `plugin-hook` — pytest lifecycle integration; `pytest_configure` hook; always-on; graceful skip when features directory absent
- `deprecation-sync` — toggle `@pytest.mark.deprecated` across all 3 stages; Gherkin tag inheritance from Rule/Feature nodes
- `auto-id-generation` — detect missing `@id` tags; write back in writable environments; fail in CI with descriptive error

### Domain Model
| Type | Name | Candidate Class/Method | In Scope |
|------|------|----------------------|----------|
| Noun | features folder path | path to `docs/features/` directory | Yes |
| Noun | `pyproject.toml` | project configuration file | Yes |
| Noun | `[tool.beehave]` section | configuration section in `pyproject.toml` | Yes |
| Noun | default path | `docs/features/` relative to project root | Yes |
| Noun | pytest plugin | `BeehavePlugin` | Yes |
| Noun | pytest session | pytest lifecycle | Yes |
| Noun | pytest config | `pytest_configure` hook | Yes |
| Noun | stub sync | full sync operation | Yes |
| Noun | `@deprecated` tag | Gherkin tag directly on an Example block | Yes |
| Noun | Gherkin tag inheritance | `@deprecated` on a `Rule:` or `Feature:` node applies to all child Examples | Yes |
| Noun | `@pytest.mark.deprecated` | pytest marker on a test function | Yes |
| Noun | Example block | Gherkin scenario | Yes |
| Noun | `@id` tag | `@id:<8-char-hex>` tag on Example | Yes |
| Noun | hex ID | 8-character lowercase hex string | Yes |
| Noun | CI environment | read-only or automated environment | Yes |
| Verb | read config | parse `[tool.beehave]` from `pyproject.toml` | Yes |
| Verb | resolve path | make the configured path absolute relative to project root | Yes |
| Verb | fall back to default | use `docs/features/` if no config present | Yes |
| Verb | register plugin | `pytest_configure` entry point | Yes |
| Verb | run before collection | invoke sync logic before collection begins | Yes |
| Verb | detect deprecated | check Example tags for `@deprecated` (direct and inherited) | Yes |
| Verb | add marker | prepend `@pytest.mark.deprecated` to test function | Yes |
| Verb | remove marker | remove `@pytest.mark.deprecated` when tag is gone | Yes |
| Verb | detect missing ID | scan Example tags for `@id` | Yes |
| Verb | generate ID | produce a unique 8-char hex string | Yes |
| Verb | write back | insert `@id` tag into `.feature` file in-place | Yes |
| Verb | fail run | abort pytest with a clear error message | Yes |

Template §3: CONFIRMED — stakeholder approved 2026-04-18

---

## Session: 2026-04-18 — Per-feature scope: multilingual-feature-parsing

### Scope
pytest-beehave delegates all language handling to gherkin-official. When a `.feature` file begins
with `# language: es`, the parser switches to Spanish keywords (Característica:, Dado:, Cuando:,
Entonces:, etc.) automatically. When it begins with `# language: zh-CN`, it switches to Chinese
keywords (功能:, 假设:, 当:, 那么:, etc.). The plugin never inspects the language directive itself.
Generated test stubs use the feature folder name for function names (always ASCII-safe slugs),
and preserve the original keyword text verbatim in docstrings. A project with mixed-language
`.feature` files works because each file is parsed in isolation.

### Feature List
- `multilingual-feature-parsing` — transparent non-English parsing via `# language: xx`; no beehave configuration needed

### Domain Model
| Type | Name | Candidate Class/Method | In Scope |
|------|------|----------------------|----------|
| Noun | `# language: xx` comment | Language directive at top of feature file | Yes |
| Noun | non-English keyword | Gherkin keyword in a supported dialect | Yes |
| Noun | pyproject.toml language config | Project-level default language setting | No |
| Noun | bad language code error handling | Custom error for unrecognised language codes | No |

Template §3: CONFIRMED — stakeholder approved 2026-04-18

---

## Session: 2026-04-18 — Per-feature scope: features-dir-bootstrap

### Scope
The features-dir-bootstrap feature ensures the Beehave plugin can always operate on a well-structured
features directory. When pytest is invoked, the plugin runs a bootstrap step as its very first action
(before stub sync). The bootstrap inspects the configured features directory and, if it exists,
ensures all three canonical subfolders (backlog/, in-progress/, completed/) are present — creating
any that are missing. It then scans for `.feature` files directly in the root features directory (not
inside any subfolder) and moves them to backlog/, making them available for stub sync in the same
pytest run. Non-`.feature` files in the root are left untouched. If a name collision occurs (a
root-level `.feature` file shares a name with an existing backlog/ file), the root-level file is left
in place and a warning is emitted. If the structure is already correct and no root-level `.feature`
files exist, the bootstrap is a complete no-op with no terminal output. If the root features
directory does not exist, the bootstrap is skipped entirely.

### Feature List
- `features-dir-bootstrap` — create missing canonical subfolders; migrate root-level `.feature` files to `backlog/`; collision warning; silent no-op when structure is correct

### Domain Model
| Type | Name | Candidate Class/Method | In Scope |
|------|------|----------------------|----------|
| Noun | features directory | root configured features path (e.g. docs/features/) | Yes |
| Noun | backlog subfolder | docs/features/backlog/ | Yes |
| Noun | in-progress subfolder | docs/features/in-progress/ | Yes |
| Noun | completed subfolder | docs/features/completed/ | Yes |
| Verb | bootstrap | create missing canonical subfolders | Yes |
| Verb | migrate | move root-level .feature files to backlog/ | Yes |
| Verb | detect | check whether the three-subfolder structure exists | Yes |

Template §3: CONFIRMED — stakeholder approved 2026-04-18

---

## Session: 2026-04-18 — Revision: remove class-based test structure

### Scope
All test stubs are top-level functions. The `class Test<RuleSlug>` wrapper discussed during initial discovery was never implemented. Conformance is two-part: (1) correct file name and (2) correct function name. No class context check exists.

### Feature List
- `stub-creation` — updated: top-level functions only, not class methods
- `stub-updates` — updated: conformance is 2-part (file + function name), not 3-part

### Domain Model
| Type | Name | Description | Change |
|------|------|-------------|--------|
| Noun | conforming test | test with correct file name AND correct function name | Updated: was 3-part (file + class context + function name), now 2-part |

---

## Session: 2026-04-19 — Feature: report-steps

### Scope
`report-steps` surfaces BDD acceptance criteria in two independent output channels: the terminal (at `-v` or above) and pytest-html reports (when `pytest-html` is installed). Both channels are scoped exclusively to tests under `tests/features/` and are independently configurable via `pyproject.toml`. Steps are always rendered verbatim from the test docstring — no reformatting. Both channels are wired into the single existing `pytest_configure` entry point. `pytest-html` is an optional install extra (`pip install pytest-beehave[html]`); when it is absent the HTML channel is silently inactive with no error raised.

Feature stages and marker state do not affect rendering — steps are shown regardless of test outcome (pass, fail, skip, error).

### Feature List
- `report-steps` — terminal steps display and HTML acceptance criteria column for `tests/features/` tests

### Domain Model
| Type | Name | Description | In Scope |
|------|------|-------------|----------|
| Noun | terminal channel | verbatim docstring printed below test path at -v or above | Yes |
| Noun | HTML channel | "Acceptance Criteria" column in pytest-html report | Yes |
| Noun | feature test | any test residing under `tests/features/` | Yes |
| Noun | non-feature test | any test outside `tests/features/` (e.g. `tests/unit/`) | Yes — explicitly excluded from output |
| Noun | verbatim steps | docstring content rendered with no reformatting | Yes |
| Verb | render steps | print/inject docstring into the appropriate output channel | Yes |
| Verb | suppress steps | omit output when channel is disabled or test is out of scope | Yes |

Template §3: CONFIRMED — stakeholder approved 2026-04-18

---

## Session: 2026-04-19 — Feature: example-hatch

### Feature List
- `example-hatch` — generate a bee-themed `docs/features/` directory tree showcasing all plugin capabilities via `pytest --beehave-hatch`; stdlib-only randomisation; respects configured features path; fails loudly on existing content unless `--beehave-hatch-force` is passed

### Domain Model
| Type | Name | Description | In Scope |
|------|------|-------------|----------|
| Noun | hatch | generated `docs/features/` directory tree with example `.feature` files | Yes |
| Noun | `--beehave-hatch` flag | pytest CLI flag that triggers hatch generation | Yes |
| Noun | `--beehave-hatch-force` flag | pytest CLI flag that allows overwriting existing hatch content | Yes |
| Noun | bee/hive-themed content | Feature names, Rule titles, Example titles, and step text using bee/hive metaphors | Yes |
| Noun | capability showcase | set of generated `.feature` files that together exercise every plugin capability | Yes |
| Noun | stdlib randomisation | use of `random` / `secrets` from Python stdlib to vary generated content | Yes |
| Verb | hatch | write the example features directory tree to the configured path | Yes |
| Verb | overwrite-protect | fail loudly when target directory already contains `.feature` files | Yes |
| Verb | force-overwrite | replace existing hatch content when `--beehave-hatch-force` is passed | Yes |
