# Discovery: pytest-beehave

## State
Status: BASELINED

## Questions
| ID | Question | Answer | Status |
|----|----------|--------|--------|
| Q1 | Who are the users? | Python developers using the python-project-template workflow who run `pytest` and want their Gherkin acceptance criteria stubs kept in sync automatically | ANSWERED |
| Q2 | What does the product do at a high level? | A pytest plugin that automatically syncs test stubs from Gherkin `.feature` files when `pytest` is run — generating IDs for un-tagged Examples, writing generic step docstrings, and applying deprecation markers | ANSWERED |
| Q3 | Why does it exist — what problem does it solve? | Removes the manual step of running `uv run task gen-tests` before every test run; ensures stubs are always in sync with acceptance criteria without developer intervention | ANSWERED |
| Q4 | When and where is it used? | During local development and CI, whenever `pytest` is invoked; operates on the `docs/features/` directory structure of the python-project-template layout | ANSWERED |
| Q5 | Success — how do we know it works? | Running `pytest` automatically syncs stubs; new Examples get IDs written back to `.feature` files; deprecated Examples get `@pytest.mark.deprecated` applied; stubs for backlog/in-progress are created/updated; completed stubs are only touched for deprecation | ANSWERED |
| Q6 | Failure — what does failure look like? | Plugin modifies test bodies or parameters; plugin breaks `pytest` collection; plugin silently corrupts `.feature` files; plugin fails in CI without a graceful fallback | ANSWERED |
| Q7 | Out-of-scope — what are we explicitly not building? | A new test runner; changes to the Gherkin parser; support for non-standard feature folder layouts; GUI or web interface; any feature not related to stub sync and ID generation | ANSWERED |
| Q8 | Should the plugin support configuration options? | Yes — custom features folder path via `pyproject.toml`; always-on (no on/off switch) | ANSWERED |
| Q9 | Auto-ID write-back in CI / read-only environments? | Fail the pytest run with an error if untagged Examples are found; all Examples MUST have an ID | ANSWERED |
| Q10 | Empty feature folders behaviour? | Skip silently — no warning | ANSWERED |
| Q11 | pytest hook timing? | Sync BEFORE collection so newly generated stubs are collected in the same run | ANSWERED |
| Q12 | "All steps" in docstrings? | Every individual step line including And/But continuations | ANSWERED |
| Q13 | Plugin location? | This repository IS the plugin (`name = "pytest-beehave"` in pyproject.toml) | ANSWERED |
| Q14 | Default marker for new stubs? | `@pytest.mark.skip(reason="not yet implemented")` — stub-sync always adds this; software-engineer adds `@pytest.mark.slow` when the test is genuinely slow | ANSWERED |
| Q15 | Test structure: plain functions or class-based? | Class-based when the feature has Rule blocks — each Rule gets `class Test<RuleSlug>` in `<rule_slug>_test.py`; features with no Rules get module-level functions in `examples_test.py` | ANSWERED |
| Q16 | What owns stub-sync markers vs software-engineer markers? | Two non-overlapping domains: stub-sync owns `skip/not-yet-implemented`, `skip/orphan`, `skip/non-conforming`, `deprecated`; software-engineer owns `slow` — crossing is prohibited | ANSWERED |
| Q17 | How is test conformance defined? | Three-part: (1) correct file name, (2) correct class context, (3) correct function name — all three must match | ANSWERED |
| Q18 | How is `@deprecated` inherited from parent Gherkin nodes? | `@deprecated` on a `Rule:` or `Feature:` node is treated as present on all child Examples for marker sync purposes | ANSWERED |
| Q19 | What library for reading/writing test files? | `libcst` — preserves formatting and comments; needs to be added as dependency | ANSWERED |

## Feature List
- `display-version` — display version from pyproject.toml
- `features-path-config` — custom features folder path via pyproject.toml
- `plugin-hook` — pytest lifecycle integration (register plugin, run before collection)
- `auto-id-generation` — detect missing @id tags, generate IDs, write back or fail in CI
- `stub-creation` — create new test stubs for backlog/in-progress; class-based layout, skip marker, docstrings
- `stub-updates` — update/rename/orphan-mark existing stubs; conformance enforcement; non-conforming redirect
- `deprecation-sync` — toggle @pytest.mark.deprecated across all 3 feature stages; Gherkin tag inheritance

## Design Decisions

### Test Structure
- Features with `Rule:` blocks: one `<rule_slug>_test.py` per Rule, each containing `class Test<RuleSlug>` with test methods
- Features with no `Rule:` blocks: single `examples_test.py` with module-level functions
- Feature-level `Background:` → `conftest.py` autouse fixture
- Rule-level `Background:` → module-level autouse fixture inside `<rule_slug>_test.py`

### Marker Ownership
Two non-overlapping ownership domains:

| Marker | Owner |
|---|---|
| `@pytest.mark.slow` | software-engineer |
| `@pytest.mark.skip(reason="not yet implemented")` | stub-sync |
| `@pytest.mark.skip(reason="orphan: no matching @id in .feature files")` | stub-sync |
| `@pytest.mark.skip(reason="non-conforming: moved to <file>::<Class>")` | stub-sync |
| `@pytest.mark.deprecated` | stub-sync |

### State Machine (stub-sync)
```
For every test_<feature_slug>_<8hex> in tests/features/<feature-name>/:
  @id hex exists in any feature file?
  NO  → orphan → add skip(reason="orphan: ...")
  YES → feature is in completed/?
        YES → frozen: only orphan detection runs (no create/update)
        NO  → in correct structure (all 3 conditions)?
              YES → update allowed: name, docstring, @pytest.mark.deprecated only
              NO  → conforming version exists?
                    YES → mark this one as non-conforming skip
                    NO  → create conforming stub first, then mark this non-conforming
```

### Conformance (3-part check)
A test is conforming if ALL THREE match:
1. Correct file (`<rule_slug>_test.py` or `examples_test.py`)
2. Correct class context (inside `class Test<RuleSlug>` or at module level)
3. Correct function name (`test_<feature_slug>_<8hex>`)

### AST Libraries
- `gherkin-official` — parse feature files (already a dependency)
- `libcst` — read/write test files preserving formatting and comments (to be added as dependency)

## References

### BDD Test Organization

- **Cucumber Official Docs — Step Organization**
  Recommends grouping step definitions by domain object, not by feature file. Warns against the "Feature-coupled step definitions" anti-pattern. One file per major domain concept.
  https://docs.cucumber.io/gherkin/step-organization/

- **Gherkin Best Practices** (andredesousa, 2022)
  Community-maintained guideline covering 25+ BDD best practices: declarative style, scenario limits per feature, tag-based organization, "features are not user stories", and multi-layered test code organization.
  https://github.com/andredesousa/gherkin-best-practices

- **Advancing BDD Software Testing: Dynamic Scenario Re-Usability and Step Auto-Complete for Cucumber Framework** (Mughal, arXiv:2402.15928, 2024)
  Academic paper demonstrating empirical improvements in test writing speed through scenario reusability and step auto-completion. Relevant to the stub-sync motivation.
  https://arxiv.org/abs/2402.15928

- **Best Practices for Cucumber Tests** (Cucumber Elixir v0.9.0)
  Practical guide covering feature file directory structure (group by domain), scenario best practices (3–7 steps), and tag-based execution filtering.
  https://hexdocs.pm/cucumber/best_practices.html

- **Complete Guide to Gherkin Syntax for BDD Testing** (TestQuality, 2026)
  Covers Scenario Outlines, Background, Data Tables, and organizational patterns including grouping by functional area, system component, or execution characteristics.
  https://testquality.com/complete-guide-to-gherkin-syntax-for-bdd-testing/

- **What's the best way to organize feature files?** (StackOverflow, 2017)
  Community discussion of directory structure patterns. Consensus: group by functional area or domain concept; feature files should be declarative and dense with business language.
  https://stackoverflow.com/questions/43226940/whats-the-best-way-to-organize-feature-files/43231594
