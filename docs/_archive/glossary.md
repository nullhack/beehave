# Glossary: pytest-beehave

Living glossary generated from the domain model in `docs/discovery.md` and architectural decisions in `docs/architecture.md`. Terms are listed alphabetically within each category.

---

## Roles

| Term | Definition |
|---|---|
| **CI Pipeline** | Automated environment (e.g. GitHub Actions) that runs pytest; treated as read-only — beehave fails fast with a descriptive error instead of writing `@id` tags back. |
| **Developer** | Python developer using the Beehave workflow; writes `.feature` files, runs pytest, reads generated test stubs. |

---

## Nouns — Domain Concepts

| Term | Definition |
|---|---|
| **`@deprecated` tag** | Gherkin tag placed directly on an `Example:`, `Rule:`, or `Feature:` node. When present, beehave applies `@pytest.mark.deprecated` to the corresponding test stub. Inheritance is resolved at parse time. |
| **`@id` tag** | `@id:<hex>` tag on a Gherkin `Example:` block that uniquely identifies it. Format: `@id:<8-char-hex>`. beehave generates and writes these back if absent (or fails in CI). |
| **`@pytest.mark.deprecated`** | pytest marker applied to a test stub when the corresponding Gherkin `Example:` carries a `@deprecated` tag (directly or via inheritance). Auto-skipped by conftest. |
| **`[tool.beehave]` section** | Configuration section in `pyproject.toml` where the developer can set `features_path` and other options. |
| **`stub_format`** | Configuration key under `[tool.beehave]` that controls output format of generated test stubs for Rule-block features. Values: `"functions"` (default, top-level functions) and `"classes"` (class-wrapped methods). First appeared: `stub-format-config`. |
| **`# language: xx` comment** | Language directive at the top of a Gherkin `.feature` file. Instructs `gherkin-official` to parse using the specified dialect (e.g. `es`, `zh-CN`). beehave delegates this fully to `gherkin-official`. |
| **`--beehave-hatch` flag** | pytest CLI flag that triggers hatch generation. When passed, beehave writes bee-themed example `.feature` files to the configured features path and exits immediately — no test collection occurs. First appeared: `example-hatch`. |
| **`--beehave-hatch-force` flag** | pytest CLI flag that allows overwriting existing hatch content. When passed alongside `--beehave-hatch`, beehave replaces any existing `.feature` files in the hatch output directories. First appeared: `example-hatch`. |
| **backlog stage** | The `docs/features/backlog/` directory. Features here receive full stub creation and updates on every pytest run. |
| **`BeehaveConfig`** | Frozen dataclass returned by `config.read_config()`; carries the resolved `features_path: Path`. |
| **bee/hive-themed content** | Feature names, Rule titles, Example titles, and step text using bee/hive metaphors. Used in hatch-generated `.feature` files to demonstrate plugin capabilities. First appeared: `example-hatch`. |
| **`BootstrapResult`** | Value object returned by `bootstrap_features_directory()`; carries lists of created directories, migrated files, and collision warnings; `is_noop` is `True` when no action was taken. |
| **capability showcase** | The set of generated `.feature` files produced by `--beehave-hatch` that together exercise every plugin capability (Background, Rule, Scenario Outline, data tables, untagged Examples, `@deprecated`). First appeared: `example-hatch`. |
| **completed stage** | The `docs/features/completed/` directory. Features here receive only orphan detection and deprecation sync — no new stubs are created, no docstrings are updated. |
| **conforming test** | A test function that satisfies both conformance rules: (1) lives in the correct file (`<rule_slug>_test.py`) and (2) has the correct function name (`test_<feature_slug>_<@id>`). |
| **default path** | `docs/features/` relative to the project root. Used when no `features_path` is set in `[tool.beehave]`. |
| **docstring** | Verbatim Gherkin step text embedded in a test stub as a Python docstring. Rendered in the terminal at `-v` and in the pytest-html Acceptance Criteria column. Never reformatted. |
| **Example block** | A Gherkin `Example:` (or `Scenario:`) node — the smallest testable unit. Each Example maps to exactly one test stub function. |
| **`ExampleId`** | 8-character lowercase hexadecimal string that uniquely identifies an `Example:` within its `.feature` file. |
| **feature slug** | The `.feature` filename stem, lowercased with hyphens replaced by underscores. Used in the generated test function name (`test_<feature_slug>_<@id>`). |
| **feature test** | Any test residing under `tests/features/`. These tests have their docstring steps surfaced in terminal and HTML output. |
| **features directory** | Root configured features path (e.g. `docs/features/`). beehave expects three canonical subfolders inside it. |
| **Gherkin tag inheritance** | When a `@deprecated` tag is placed on a `Rule:` or `Feature:` node, all child `Example:` nodes inherit it. Resolved at parse time by `feature_parser.py`. |
| **hatch** | The generated `docs/features/` directory tree with bee-themed example `.feature` files. Written by `hatch.py` when `--beehave-hatch` is passed. First appeared: `example-hatch`. |
| **`HatchFile`** | Frozen dataclass carrying `relative_path: str` and `content: str`; returned by `generate_hatch_files()` and consumed by `write_hatch()`. Separates pure content generation from filesystem writes. First appeared: `example-hatch`. |
| **hex ID** | See `ExampleId`. |
| **HTML channel** | The "Acceptance Criteria" column in the pytest-html report, populated with each feature test's docstring. Active only when `pytest-html` is installed and `show_steps_in_html` is not `false`. |
| **in-progress stage** | The `docs/features/in-progress/` directory. Features here receive full stub creation and updates on every pytest run. |
| **non-English keyword** | A Gherkin keyword in a supported dialect (e.g. `Característica:`, `功能:`). beehave preserves these verbatim in generated docstrings. |
| **non-feature test** | Any test outside `tests/features/` (e.g. `tests/unit/`). Steps are never rendered for non-feature tests. |
| **orphan test** | A test function with no matching `@id` in any `.feature` file in the features directory. |
| **`ParsedExample`** | Domain object produced by `feature_parser`; carries `example_id`, `rule_slug`, `feature_slug`, `steps`, and `is_deprecated`. |
| **`ParsedFeature`** | Domain object produced by `feature_parser`; carries the feature slug, stage, and a list of `ParsedExample` objects. |
| **pytest config** | The pytest configuration object provided to `pytest_configure`; used to resolve the project root and access the terminal writer. |
| **pytest plugin** | The `BeehavePlugin` class registered via the `pytest11` entry point in `pyproject.toml`. Loaded automatically by pytest on every invocation. |
| **pytest session** | The pytest lifecycle object; beehave's sync runs inside `pytest_configure` (before collection) so newly generated stubs are collected in the same run. |
| **rule slug** | The `Rule:` title slugified to lowercase with underscores. Used as the test file name (`<rule_slug>_test.py`) and as part of the test function name. |
| **stdlib randomisation** | Use of `secrets.choice()` from the Python standard library to vary generated hatch content. No external dependencies required. First appeared: `example-hatch`. |
| **stub sync** | The full synchronisation operation: parse features, compare against existing stubs, create/rename/orphan/deprecate as needed. |
| **terminal channel** | Verbatim docstring printed below the test path in terminal output at `-v` or above, for feature tests only. |
| **test file** | `<rule_slug>_test.py` (one per `Rule:` block) generated in `tests/features/<feature_slug>/`. |
| **test stub** | A top-level Python function `test_<feature_slug>_<@id>()` with a `@pytest.mark.skip(reason="not yet implemented")` decorator and a verbatim Gherkin docstring. |
| **verbatim steps** | Docstring content rendered with no reformatting — exactly as written in the `.feature` file. |

---

## Nouns — Directory / File Paths

| Term | Definition |
|---|---|
| **backlog subfolder** | `docs/features/backlog/` — features queued for development. |
| **completed subfolder** | `docs/features/completed/` — accepted and shipped features. |
| **in-progress subfolder** | `docs/features/in-progress/` — the one feature currently being built (WIP limit: 1). |
| **`pyproject.toml`** | Python project configuration file. beehave reads `[tool.beehave].features_path` from it using `stdlib tomllib`. |

---

## Verbs — Operations

| Term | Definition |
|---|---|
| **add marker** | Prepend `@pytest.mark.deprecated` to a test function when the Example is deprecated. |
| **bootstrap** | Create the three canonical subfolders (`backlog/`, `in-progress/`, `completed/`) if any are missing. Runs before stub sync. |
| **create stub** | Write a new top-level `test_<feature_slug>_<@id>()` function for a new `Example:` block. |
| **deprecate stub** | Apply `@pytest.mark.deprecated` to a test function when the corresponding Gherkin `Example:` carries `@deprecated`. |
| **detect** | Check whether the three-subfolder structure exists; used to decide whether bootstrap action is needed. |
| **detect deprecated** | Check `Example:` tags (direct and inherited) for `@deprecated`. |
| **detect missing ID** | Scan `Example:` tags for a valid `@id:<hex>` tag; flag if absent. |
| **fail run** | Abort pytest with a clear, descriptive error message (used in CI when `@id` tags are absent). |
| **fall back to default** | Use `docs/features/` if no `features_path` is set in `[tool.beehave]`. |
| **force-overwrite** | Replace existing hatch content when `--beehave-hatch-force` is passed. First appeared: `example-hatch`. |
| **generate ID** | Produce a unique 8-character lowercase hex string, unique within the current `.feature` file. |
| **hatch** | Write the example features directory tree to the configured path. Triggered by `--beehave-hatch`. First appeared: `example-hatch`. |
| **mark non-conforming** | Apply `@pytest.mark.skip(reason="non-conforming: moved to <file>")` to a test function that is in the wrong file or has the wrong name. The conforming stub is always created first. |
| **mark orphan** | Apply `@pytest.mark.skip(reason="orphan: ...")` to a test function with no matching `@id` in any `.feature` file. |
| **migrate** | Move a root-level `.feature` file found directly in the features directory into `backlog/`. |
| **overwrite-protect** | Fail loudly when the target hatch directory already contains `.feature` files and `--beehave-hatch-force` was not passed. First appeared: `example-hatch`. |
| **read config** | Parse `[tool.beehave]` from `pyproject.toml` using `stdlib tomllib`; return a `BeehaveConfig`. |
| **register plugin** | The `pytest_configure` entry point that loads `BeehavePlugin` into the pytest session. |
| **remove marker** | Remove `@pytest.mark.deprecated` from a test function when the `@deprecated` tag is no longer present. |
| **render steps** | Print or inject the docstring into the appropriate output channel (terminal or HTML). |
| **resolve path** | Make the configured `features_path` absolute relative to the project root. |
| **run before collection** | Invoke stub sync inside `pytest_configure` so new stubs are discoverable in the same pytest run. |
| **suppress steps** | Omit step output when the channel is disabled (`show_steps_in_terminal = false` / `show_steps_in_html = false`) or the test is outside `tests/features/`. |
| **write back** | Insert a generated `@id:<hex>` tag into the `.feature` file in-place, on the line immediately before the `Example:` keyword. |
| **select format** | Choose between `"functions"` (top-level) and `"classes"` (class-wrapped) format based on `stub_format` config. First appeared: `stub-format-config`. |
| **wrap class** | Output a test function as a method inside `class Test<RuleSlug>:` when `stub_format = "classes"`. First appeared: `stub-format-config`. |
