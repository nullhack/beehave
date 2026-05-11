# IN_20260510_cli_commands — CLI Commands: sync, generate, fix, clean

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Project Founder
> **Session type:** Domain deep-dive

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | Designing beehave's four CLI commands for managing the relationship between .feature files and Python test files: sync, generate, fix, clean. Each command does ONE thing with clear risk level. |
| Q2 | What is the core design principle? | "Report first, explicit flags for actions." The default behavior of every command is to report. Destructive or modifying actions require explicit opt-in. The risk level is clear from the command name: sync (safe/additive), generate (safe/additive), fix (moderate/modifies), clean (destructive/deletes). |
| Q3 | What is the ownership model? | .feature files are the source of truth. beehave owns @id tags in .feature files (only beehave writes them). Python test files are derived artifacts — beehave can create, fix, and clean them to match the source. Developers own function bodies; beehave owns decorator text and function signatures. |

## `beehave sync`

| ID | Question | Answer |
|----|----------|--------|
| Q4 | What does `beehave sync` do? | (1) Parse all .feature files. (2) Find scenarios without @id tags → generate 8-character random IDs and write them into the .feature files. (3) Find scenarios with malformed or non-standard @id tags → replace with beehave-generated IDs. (4) Report orphan scenarios and orphan tests. |
| Q5 | What is the ID format? | `@id:` followed by an 8-character random ID. Example: `@id:kx7m2p9q`. IDs are generated once by `beehave sync` and are permanent — editing scenario text does NOT change the ID. Re-running sync only generates IDs for scenarios that don't have one. |
| Q6 | Does beehave own @id tags? | **Yes.** beehave owns @id tags entirely. If a developer manually writes `@id:my_custom_name`, beehave sync will replace it with a beehave-generated 8-char random ID. Manual @id tags are not preserved. This ensures consistency and avoids collisions. |
| Q7 | Is sync idempotent? | Yes. Running sync twice produces the same .feature files as running once. Already-tagged scenarios keep their IDs (random IDs are permanent once generated). |
| Q8 | Risk level? | **Safe (additive).** Sync only adds @id tags to .feature files. It does not modify scenario text, restructure features, or delete anything. |

## `beehave generate`

| ID | Question | Answer |
|----|----------|--------|
| Q9 | What does `beehave generate` do? | Create test stub files for orphan scenarios (scenarios with @id that have no matching Python test function). |
| Q10 | What if the target file already exists? | Warn that the file exists, then offer an interactive prompt: "balance_accounting/default_test.py already exists. Add function? [y/N]". If yes, append the new function to the end of the existing file. |
| Q11 | What if a function with the same @id already exists? | Skip with warning: "function for @id:a1b2c3d4 already exists". Generate is idempotent — running twice is safe. |
| Q12 | What does a generated stub look like? | Includes: imports (hypothesis strategies, beehave decorators, pytest), module-level strategy variables for all `<placeholders>` (defaulting to `st.integers()`), @Given/@When/@Then/@And/@But decorators matching .feature steps, @Example decorators from .feature Examples table (if any), `@pytest.mark.skip(reason="not yet implemented")` decorator, function with `raise NotImplementedError` body. Function name follows `test_<scenario_title_snake_case>_<id>` pattern. *(Updated per IN_20260511_self_validation_pain_points PP4.)* |
| Q13 | Risk level? | **Safe (additive).** Generate creates new files or appends functions to existing files. It does not modify existing functions or delete anything. |

## `beehave fix`

| ID | Question | Answer |
|----|----------|--------|
| Q14 | What does `beehave fix` do? | Fix decorator text mismatches between .feature steps and Python test decorators, and add missing step decorators. |
| Q15 | What is the scope of fix? | Two operations: (1) Fix text in existing decorators that match 1-1 by position — if .feature says `Given a user with balance <initial>` but the test says `@Given("a user with an balance <initial>")`, fix corrects the decorator text to match .feature exactly. (2) Add missing step decorators — if .feature has 3 steps but the test only has 2, fix adds the missing decorator(s) and adds the corresponding `<placeholder>` names to the function parameters. |
| Q16 | What does fix NOT do? | Fix does NOT: remove extra decorators (that's the developer's call), modify function bodies (the developer owns those), rename functions, or change strategy variables. |
| Q17 | How are missing decorators added? | @And and @But are aliases for @When or @Then — they carry no additional behavior beyond step text validation and ordering. When fix adds a missing decorator, it adds it with the correct Gherkin keyword from the .feature file. The function parameters are updated to include any new `<placeholder>` names from the added decorator. |
| Q18 | Does fix require confirmation? | No interactive confirmation, but `beehave fix --dry-run` shows what would be changed without modifying files. |
| Q19 | Risk level? | **Moderate (modifies).** Fix changes decorator text in existing Python files and adds missing decorators. It does not delete code or modify function bodies. |

## `beehave clean`

| ID | Question | Answer |
|----|----------|--------|
| Q20 | What does `beehave clean` do? | Remove orphan test functions — Python test functions whose @id suffix has no matching .feature scenario. |
| Q21 | What does "remove" mean exactly? | Delete the function from the file. Not comment out, not `@pytest.mark.skip` — actually remove it. |
| Q22 | What about strategy variables only used by the removed function? | Left in the file. Clean removes the function, not unused variables. Linters handle unused imports/variables. |
| Q23 | What about empty files? | If removing a function leaves a file with no test functions, the file is NOT deleted. It may still contain strategy variables, imports, or helper functions. |
| Q24 | Does clean require confirmation? | **Yes.** `beehave clean` lists orphan tests and asks "Remove N orphan tests? [y/N]". `beehave clean --force` skips confirmation (for CI/scripts). |
| Q25 | Risk level? | **Destructive (deletes).** Clean removes code. Confirmation is required by default. |

## Cross-cutting Concerns

| ID | Question | Answer |
|----|----------|--------|
| Q26 | Do all commands support `--dry-run`? | `--dry-run` is supported for `fix` and `clean` (the modifying/destructive commands). Not needed for `sync` and `generate` since they're additive (safe). |
| Q27 | Do all commands support `--json` output? | Yes. All commands support `--json` for programmatic consumption. Human-readable by default, machine-readable on request. |
| Q28 | What are the exit codes? | 0 = success, no issues. 1 = errors found (orphans in strict mode, validation failures). 2 = warnings found but no errors. |
| Q29 | What about tests without @id suffix? | Tests with beehave decorators but no @id suffix cannot be matched to a specific .feature scenario. beehave sync reports this as informational: "test `test_user_balance` has beehave decorators but no @id suffix. Add an @id suffix to enable .feature validation, or this test operates at adoption level 1." This is NOT a warning or error — it's a valid state (adoption level 1). |
| Q30 | How do the commands interact? | Typical workflow: (1) `beehave sync` — assign @id tags to .feature scenarios. (2) `beehave generate` — create test stubs for new scenarios. (3) Developer writes test bodies. (4) `beehave fix` — correct any decorator drift. (5) `beehave clean` — remove orphan tests after refactoring. Commands are independent and idempotent — they can be run in any order, any number of times. |

## Consistency Check

| ID | Question | Answer |
|----|----------|--------|
| Q31 | Is the "report first, explicit flags for actions" principle consistent? | Yes. `sync` reports + adds @id tags (its sole purpose). `generate` reports orphans + creates stubs with interactive confirmation for existing files. `fix` reports mismatches + fixes them with `--dry-run` available. `clean` reports orphans + deletes with interactive confirmation. The more destructive the action, the more confirmation required. |
| Q32 | Is the ownership model consistent? | Yes. .feature files: beehave owns @id tags (sync adds/replaces them). Python test files: developers own function bodies; beehave owns decorator text (fix corrects it) and function signatures for missing steps (fix adds parameters). Neither side auto-modifies the other's primary content — .feature step text is never changed by beehave, function bodies are never changed by beehave. |
| Q33 | Is the additive/destructive risk model consistent? | Yes. sync and generate are additive (create data, don't modify existing content). fix is moderate (modifies decorator text and adds missing decorators, doesn't delete). clean is destructive (deletes functions). The commands escalate in risk: sync → generate → fix → clean. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Idempotency | When any command is run twice, the result is the same as running once | sync, generate, fix, and clean all produce idempotent results | Must |
| QA2 | Safety | When a developer runs a command without flags, no destructive action occurs | sync and generate are safe by default; fix reports and applies with dry-run option; clean requires confirmation | Must |
| QA3 | Discoverability | When a scenario or test is orphaned, the developer knows exactly what to do | Commands report actionable information: which scenarios need stubs, which tests are orphaned, which decorators are mismatched | Must |
| QA4 | Reversibility | When fix or clean makes an unwanted change, the developer can undo it | Changes are version-controlled (git). fix and clean modify tracked files — `git diff` shows what changed, `git checkout` reverts. | Should |

---

## Pain Points Identified

- Without CLI commands, developers would manually manage @id tags and step text alignment — tedious and error-prone
- Auto-editing existing Python code is risky, but leaving all fixes manual defeats the purpose of the tool
- The balance is: beehave can fix decorator text and add missing decorators (mechanical, source-of-truth-driven), but never modifies function bodies (developer-owned logic)

## Business Goals Identified

- Provide a clear, safe CLI workflow: sync → generate → fix → clean, with escalating risk and appropriate safeguards
- Make .feature files the source of truth — beehave synchronizes Python test files to match, never the reverse
- Keep commands composable and idempotent — each command does one thing well, can be run in any order, and produces consistent results on re-run

## Terms to Define (for glossary)

- **`beehave sync`** — Assigns @id tags to .feature scenarios that lack them, replaces malformed @id tags with beehave-generated IDs, and reports orphans. Safe and idempotent.
- **`beehave generate`** — Creates test stub files for orphan scenarios. Warns if the target file exists and offers to append. Safe and idempotent.
- **`beehave fix`** — Corrects decorator text to match .feature step text and adds missing step decorators. Moderate risk (modifies existing files). Supports `--dry-run`.
- **`beehave clean`** — Removes orphan test functions. Destructive (deletes code). Requires interactive confirmation by default; `--force` skips confirmation.
- **Random permanent ID** — An 8-character randomly generated ID assigned once by `beehave sync` and never changed. Editing scenario text does not affect the ID. Not derived from scenario content. *(Updated per IN_20260510_adversarial_review R1: changed from content-hash to random permanent.)*
- **Orphan test** — A Python test function whose @id suffix has no matching .feature scenario.
- **Orphan scenario** — A .feature scenario whose @id has no matching Python test function.

## Updates to Previous INs

### IN_20260510_collection_mechanics

- **Q6** (ID generation format): Resolved — 8-character random permanent IDs, generated once by `beehave sync`. Not content-hash. *(Updated per IN_20260510_adversarial_review R1.)*
- **Q8** (file structure): Confirmed — `<feature_name>/<rule_name>_test.py` or `<feature_name>/default_test.py`.
- **D2** (@example auto-generation): Resolved — `beehave generate` creates @Example decorators from .feature Examples table rows.
- **D6** (multiple .feature files per directory): Deferred — not yet decided.

### IN_20260510_sync_and_io

- **Q18** (beehave sync scope): Updated — sync now also replaces malformed or non-standard @id tags with beehave-generated IDs. beehave owns all @id tags.
- **Q19** (test stubs): Resolved — `beehave generate` is a separate command. It creates test stubs for orphan scenarios.
- **Q20** (stale @id detection): Resolved — `beehave fix` handles decorator text mismatches. `beehave clean` handles orphan removal.

### IN_20260510_step_decorator_runtime

- No updates from this session.

### IN_20260510_settings_and_defaults

- No updates from this session.

## Action Items

- [ ] Design the content-hash algorithm for @id generation (ensure 8 chars is collision-resistant enough for typical projects)
- [ ] Design the stub template format (imports, strategy variables, decorators, function signature, `...` body)
- [ ] Design the `--json` output schema for each command
- [ ] Define the `pyproject.toml` schema including `feature_paths`, `strict`, `max_examples`
- [ ] Decide on multiple .feature files per feature directory
- [ ] Investigate how `beehave fix` adds missing function parameters to existing signatures (AST manipulation)