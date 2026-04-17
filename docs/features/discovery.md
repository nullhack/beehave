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
| Q14 | Default marker for new stubs? | No default marker — developers choose unit or integration when implementing | ANSWERED |

## Feature List
- `plugin-hook` — pytest lifecycle integration (register plugin, run before collection)
- `auto-id-generation` — detect missing @id tags, generate IDs, write back or fail in CI
- `stub-sync` — create/update test stubs for backlog/in-progress (names, docstrings, markers)
- `deprecation-sync` — toggle @pytest.mark.deprecated across all 3 feature stages
- `plugin-configuration` — custom features folder path via pyproject.toml
