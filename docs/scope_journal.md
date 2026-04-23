# Scope Journal: beehave

> Raw Q&A record from discovery sessions.
> Append-only: never edit or remove past entries.

---

## 2026-04-21 — Session 1

### General

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
| C9 | Test stub ownership: When beehave updates a test stub file, how does it avoid overwriting developer-written code? | Features map from source folder (`docs/features/` by default, configurable) to `tests/features/<feature_snake_name>/`. Each test function carries the `@id` in its name (`test_<feature_slug>_<id>`), making identification unambiguous. Feature files can live in four locations — `docs/features/backlog/`, `docs/features/in-progress/`, `docs/features/completed/`, and `docs/features/` (root-level). All four map identically to the same `tests/features/<feature_snake_name>/` directory. |
| C10 | Feature stages (backlog/in-progress/completed): Does beehave handle these three directories differently? | No behavioral difference. After `beehave nest`, all three folders exist but features in any of them map identically to `tests/features/<feature_snake_name>/`. Root-level `.feature` files also map identically. |

### Architectural Cross-cutting (Gaps)

| ID | Question | Status |
|----|----------|--------|
| A1 | Error handling patterns | Unanswered |
| A2 | Performance constraints | Unanswered |
| A3 | Versioning and backwards compatibility | Unanswered |
| A4 | Logging and observability | Unanswered |

### Per-feature

See `discovery.md` for the full per-feature Q&A (N1–N11, I1–I7, S1, CA1–CA2, T1–T3, SC1–SC3, SU1–SU3, SCL1–SCL5, AC1–AC3, PA1–PA6, PH1–PH2, UA1).

### Supplement (2026-04-21)

| Feature | Question | Answer |
|---------|----------|--------|
| `deprecation-sync` | Does `@deprecated` cascade from Feature/Rule to child Examples? | Yes — cascade is absolute. A `@deprecated` tag on a Feature or Rule applies to all Examples beneath it. There is NO override mechanism in v1. |
| `hatch` | What should generated demo content look like? | One or two bee-themed `.feature` files covering common Gherkin patterns (Feature, Rule, Example, Scenario Outline). Enough to demo the full sync workflow end-to-end. |
