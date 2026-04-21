# Discovery Journal: beehave

---

## 2026-04-21 — Session 1
Status: IN-PROGRESS

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
| Q7 | Out-of-scope — what are we explicitly not building? | Not doing any coding (i.e. not modifying test implementation bodies). There is a configurable structure for tests, and that structure will be followed. Parameters should be handled the way each target framework treats them natively. Outlines should show completely in docstrings/templates per framework. |
| Q8 | What is the public API surface — CLI, Python API, or both? | Both CLI and Python API. Commands have a subtle bee-world-related flavor. CLI commands selected: `beehave sync`, `beehave status`, `beehave version`, `beehave nest`, `beehave hatch`. Flags: `--overwrite`. |
| Q9 | How do consumers (like pytest-beehave) register marker templates? | Stubs and changes will be templated per framework adapter. Start with pytest only, then add unittest. The difference between adapters is mostly marker style and framework conventions. |
| Q10 | Who configures beehave — end developers or framework authors? | End developers. Framework authors can use it if they want to integrate, but that is not the primary concern. |
| Q11 | What is the exact relationship between `beehave` and the future `pytest-beehave` wrapper? | `pytest-beehave` is a pytest-only wrapper using `beehave` under the hood. It adds specific pytest capabilities like automatic running, HTML acceptance criteria injection, and terminal acceptance criteria. |
| Q8-CLI-diff | What is the difference between bootstrap and generate? | `nest`/`init` is project directory setup; `hatch`/`example` is demo content generation. |

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
| C9 | Test stub ownership: When beehave updates a test stub file, how does it avoid overwriting developer-written code? | Features map from source folder (`docs/features/` by default, configurable) to `tests/features/<feature_snake_name>/`. Each test function carries the `@id` in its name (`test_<feature_slug>_<id>`), making identification unambiguous. |
| C10 | Feature stages (backlog/in-progress/completed): Does beehave handle these three directories differently? | No behavioral difference. After `beehave nest`, all three folders (`backlog/`, `in-progress/`, `completed/`) exist but features in any of them map identically to `tests/features/<feature_snake_name>/`. The structure is independent of which folder the `.feature` file lives in. |

### Per-feature
Status: IN-PROGRESS


## 2026-04-21 — Session 1
Status: IN-PROGRESS

### General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | Who are the users? | Developers, testers and managers that use BDD as part of their development cycle. The tool should be extensible to other test frameworks (framework-agnostic), installable via extras like `pip install beehave[pytest]`, `pip install beehave[unittest]`, etc. Wrappers (e.g. `pytest-beehave`) can be developed on each framework for deeper integration, but that level of integration is out of scope. |
| Q2 | What does the product do at a high level? | Beehave keeps the living documentation reasonably up to date. It does not check implementation specifics or change test bodies. It flags, changes, and updates whatever is mandatory, following the mantra that `.feature` files are the source of truth and `tests/` should reflect that. |
| Q3 | Why does it exist — what problem does it solve? | It is too complicated to keep living documentation and code/tests in sync. Beehave tries to make that gap smaller. |
| Q4 | When and where is it used? | It can be used as a package, and it should also have CLI capabilities. |
| Q5 | Success — what does "done" look like? | Success is when stubs are generated and updated without destroying anything, and when the tool successfully informs the user when something changed that is beyond the scope of the project to handle. |
| Q6 | Failure — what must never happen? | Failure is when it breaks the user tests or fails to inform the user about something. Users must still be able to force changes and see dry-run changes. |
| Q7 | Out-of-scope — what are we explicitly not building? | Not doing any coding (i.e. not modifying test implementation bodies). There is a configurable structure for tests, and that structure will be followed. Corner cases like parameters need more thought — the stakeholder is unsure what to do with them. |
| Q8 | What is the public API surface — CLI, Python API, or both? | Both CLI and Python API. Commands should have a subtle bee-world-related flavor, but not overdone — only used when it feels natural. |
| Q9 | How do consumers (like pytest-beehave) register marker templates? | Stubs and changes will be templated per framework adapter. Start with pytest only, then add unittest. The difference between adapters is mostly marker style and framework conventions (e.g. behave splits into steps; in pytest one function or class can be used depending on the desired template). |
| Q10 | Who configures beehave — end developers or framework authors? | End developers. Framework authors can use it if they want to integrate, but that is not the primary concern. The primary concern is keeping living documentation in sync. |
| Q11 | What is the exact relationship between `beehave` and the future `pytest-beehave` wrapper? | `pytest-beehave` is a pytest-only wrapper using `beehave` under the hood. It adds specific pytest capabilities like automatic running, HTML acceptance criteria injection, and terminal acceptance criteria. |
| Q4-FU | Clarification: What are the exact usage modes for the package and CLI? | Python API: `from beehave import ...`; CLI: `beehave --<keywords>` from bash. |
| Q7-FU | Clarification: How should Scenario Outlines and parameters be handled? | Parameters should be handled the way each target framework treats them natively. Outlines should still show completely in docstrings/templates, but parameter substitution should follow native framework conventions (e.g., pytest parametrize). |
| Q8-CLI | Stakeholder CLI command selections | `beehave sync` (generate/sync stubs), `beehave status` (dry-run/check), `--overwrite` flag (force overwrite), `beehave version` (version/info), `beehave nest` (bootstrap/init project structure), `beehave hatch` (generate example/demo content). |
| Q8-CLI-diff | What is the difference between bootstrap and generate? | `nest`/`init` is project directory setup; `hatch`/`example` is demo content generation. |

**General: COMPLETE**

### Cross-cutting

Status: COMPLETE

| ID | Question | Answer |
|----|----------|--------|
| C1 | Framework detection: How does beehave know which test framework a project uses? Auto-detect (look for `pytest.ini`, `unittest` imports, etc.), require explicit configuration, or support both? | No auto-detect. Explicit `--framework <name>` flag (defaults to `pytest`). |
| C2 | When does beehave run? Is beehave strictly on-demand (developer runs CLI when they want), or should it support automatic triggers like filesystem watch mode, git pre-commit hooks, or running as part of test discovery? | On-demand only (developer runs CLI when they want). No watch mode, no pre-commit hooks, no auto-triggers. |
| C3 | Configuration source: Where does beehave read its configuration from? `pyproject.toml` under `[tool.beehave]`? A dedicated config file? Environment variables? CLI flags only? All of the above with precedence? | `pyproject.toml` under `[tool.beehave]`. |
| C4 | Feature file mutability: Are `.feature` files strictly read-only source of truth for beehave? Or are there scenarios where beehave writes to a `.feature` file (e.g., adding `@id` tags, reordering scenarios)? | Beehave writes to `.feature` files ONLY to add `@id` tags to Examples that have no ID. Nothing else is modified. |
| C5 | Deletion handling: What happens when a `.feature` file is deleted? Should beehave delete the corresponding test stub, warn the user that an orphan exists, or leave it entirely to the user? | Warn by default when a `.feature` file is deleted. Configurable in `pyproject.toml` to raise an error instead. |
| C6 | Multi-framework projects: Can a single project use multiple test frameworks simultaneously, or is beehave strictly one adapter per project? | One framework per invocation (`--framework <name>`). Generated stubs are for that framework only. Only generates stubs for Examples without a corresponding existing test (identified by `@id` in test function name). |
| C7 | Template customization: Can end users override or customize the templates that adapters use to generate stubs? Or are templates fixed and versioned with the adapter? | Yes — users can point to a custom template folder. |
| C8 | CLI output style: What should the terminal output look like? Silent by default (Unix philosophy), verbose with `--verbose`, or always show a summary? Should `beehave status` emit machine-readable output (JSON) for CI integration? | Silent by default (Unix philosophy). `--verbose` for human-readable output. `--json` for machine-readable output (CI integration). |
| C9 | Test stub ownership: When beehave updates a test stub file, how does it avoid overwriting developer-written code? Does it only touch functions matching a specific naming convention? Does it add section comments delimiting "auto-generated vs hand-written"? | Features map from source folder (`docs/features/` by default, configurable) to `tests/features/<feature_snake_name>/`. Each test function carries the `@id` in its name (`test_<feature_slug>_<id>`), making identification unambiguous. |
| C10 | Feature stages (backlog/in-progress/completed): Does beehave handle these three directories differently, or are they just organizational folders with no behavioral differences in stub generation? | No behavioral difference. After `beehave nest`, all three folders (`backlog/`, `in-progress/`, `completed/`) exist but features in any of them map identically to `tests/features/<feature_snake_name>/`. The structure is independent of which folder the `.feature` file lives in. |

**Cross-cutting: COMPLETE**

### Per-feature discovery
Status: IN-PROGRESS
