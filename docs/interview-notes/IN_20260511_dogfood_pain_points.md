# IN_20260511_dogfood_pain_points — Dogfood Exercise: 6 Pain Points in generate()

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Dogfood Tester
> **Session type:** Feature specification

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | A dogfood exercise: using beehave's own `generate()` command to produce test stubs from `docs/features/decorator_test.feature`. Six pain points were discovered and documented as post-mortems (PM_20260511_*). This session extracts them into structured interview notes for prioritization and action. |
| Q2 | What was the exercise? | (1) Write `docs/features/decorator_test.feature` with multiple scenarios. (2) Run `beehave sync` to assign @id tags. (3) Run `beehave generate` to create stubs. (4) Write test bodies using beehave's step decorators. (5) Run `pytest` to verify end-to-end. |
| Q3 | What is the reference for expected behavior? | IN_20260510_cli_commands Q12 defines the stub template: imports, strategy variables, step decorators matching .feature steps, @Example decorators, function with `...` body. The project's own TDD convention (used in all existing tests) uses `@pytest.mark.skip(reason="not yet implemented")` and `raise NotImplementedError` for stubs. |

## Pain Point: Empty File Paths in generate() Output

| ID | Question | Answer |
|----|----------|--------|
| PP1-Q1 | What did the tester experience? | Running `generate()` in text mode produced output like "Created  for @a1b2c3d4" — the file path was an empty string. The tester could not tell which files were created or where. |
| PP1-Q2 | What is the expected behavior? | Output should read "Created tests/features/decorator_test/default_test.py for @a1b2c3d4" — the human-readable output must show the actual file path so developers can locate generated stubs. |
| PP1-Q3 | What is the gap? | Key mismatch: `_process_scenario()` returns `{'file': '...'}` but `_format_text_output()` reads `r.get('test_file', '')`. The wrong key produces empty strings. (Source: PM_20260511_generate_empty_file_paths) |
| PP1-Q4 | Fix recommendation? | **Must.** Align the dict keys (either `test_file` or `file` — pick one). Add a test that calls `generate()` in text mode and asserts the output contains the expected file path. This is a broken user-facing output — it must be fixed before generate() is usable. |

## Pain Point: Repeated Import Blocks When Appending Scenarios

| ID | Question | Answer |
|----|----------|--------|
| PP2-Q1 | What did the tester experience? | After generating stubs for a feature with 3+ scenarios, the output file `default_test.py` contained three identical import blocks — `from beehave.decorators import ...`, `from hypothesis import strategies as st`, strategy variable declarations — repeated once per scenario. |
| PP2-Q2 | What is the expected behavior? | One import block at the top of the file, followed by all test functions. IN_20260510_cli_commands Q10 specifies append behavior: "Add function? [y/N]" → append the new function to the end. Appending should add the function, not re-emit imports. |
| PP2-Q3 | What is the gap? | `_generate_stub_content()` always produces a self-contained Python file. `_append_function_stub()` concatenates the full stub content to the existing file. No logic strips imports from appended content. (Source: PM_20260511_generate_repeated_imports) |
| PP2-Q4 | Fix recommendation? | **Must.** Either: (1) pass an `is_append` flag to `_generate_stub_content()` that omits imports, or (2) have `_append_function_stub()` strip leading import/comment lines when the target file already contains them. Add a test that generates two scenarios into the same file and asserts the import block appears exactly once. Generated code must be clean, not embarrassing. |

## Pain Point: Generated Test Directories Missing __init__.py

| ID | Question | Answer |
|----|----------|--------|
| PP3-Q1 | What did the tester experience? | `generate()` created `tests/features/decorator_test/default_test.py` but no `tests/features/decorator_test/__init__.py`. Some pytest configurations fail to collect tests from directories without `__init__.py`. |
| PP3-Q2 | What is the expected behavior? | Generated test directories should be proper Python packages with `__init__.py`. The project's own convention (visible in `tests/features/`) uses `__init__.py` in every test package. |
| PP3-Q3 | What is the gap? | `_ensure_test_directory()` calls `os.makedirs()` but never creates `__init__.py`. It only ensures the directory exists. (Source: PM_20260511_generate_no_init_py) |
| PP3-Q4 | Fix recommendation? | **Should.** After `os.makedirs()`, create an empty `__init__.py` if it doesn't already exist. Simple fix: `Path(os.path.join(dir, "__init__.py")).touch()`. While some pytest configurations work without it, creating it is zero-cost and prevents subtle collection failures. |

## Pain Point: Generated Stubs Pass Silently Instead of Skipping

| ID | Question | Answer |
|----|----------|--------|
| PP4-Q1 | What did the tester experience? | Running `pytest` on generated stubs showed all tests as PASSED (green). The stubs use `...` (Ellipsis) as the function body, which is a valid no-op expression in Python. The tester got false confidence that unimplemented behavior was tested. |
| PP4-Q2 | What is the expected behavior? | (1) The project's own TDD convention: `@pytest.mark.skip(reason="not yet implemented")` + `raise NotImplementedError`. (2) IN_20260510_cli_commands Q12 specifies `...` body, but the intent is that stubs should be clearly unimplemented. Stubs must not silently pass. |
| PP4-Q3 | What is the gap? | `_generate_stub_content()` produces `def test_foo(): ...` with no skip marker. Ellipsis is a valid expression that returns `None` — the test passes immediately. The project contradicts its own convention. (Source: PM_20260511_generate_stub_no_skip_marker) |
| PP4-Q4 | Fix recommendation? | **Must.** Add `import pytest` and `@pytest.mark.skip(reason="not yet implemented")` decorator, and change the body to `raise NotImplementedError`. This prevents false-green test suites. Update IN_20260510_cli_commands Q12 to reflect this change: the stub body should be `raise NotImplementedError`, not bare `...`. |

## Pain Point: Generated Stubs Omit Step Decorators

| ID | Question | Answer |
|----|----------|--------|
| PP5-Q1 | What did the tester experience? | Generated stub `def test_adding_nectar_to_the_honey_store_a1b2c3d4()` had no `@Given`, `@When`, `@Then` decorators. The stub was a bare function that didn't use beehave's core decorator mechanism — the entire value proposition of the library. |
| PP5-Q2 | What is the expected behavior? | IN_20260510_cli_commands Q12 explicitly states: stubs include "@Given/@When/@Then/@And/@But decorators matching .feature steps". The generate command's primary job is to produce a usable starting point wired to the feature file. |
| PP5-Q3 | What is the gap? | `_process_scenario()` passes `steps=[]` and `examples=[]` to `_generate_stub_content()`. The step extraction logic exists in `_parse_feature_steps()` but is not connected to the generate flow. The decorator-producing code (cli.py lines 199-215) is dead code. (Source: PM_20260511_generate_no_step_decorators) |
| PP5-Q4 | Fix recommendation? | **Must.** Connect `_parse_feature_steps()` to `_process_scenario()` so that steps are extracted from the feature file and passed to `_generate_stub_content()`. The function already handles step decoration — it just needs non-empty input. This is the core value of generate(). Without it, the command produces glorified empty functions. |

## Pain Point: Silent Strategy Fallback Produces Surprising Values

| ID | Question | Answer |
|----|----------|--------|
| PP6-Q1 | What did the tester experience? | A test with `<parts>` placeholder where no `parts_strategy` was defined silently fell back to `st.integers()`, which generated 0, negative numbers, and any integer. This caused `ZeroDivisionError` and confusing assertion failures that didn't match the test's intent. |
| PP6-Q2 | What is the expected behavior? | IN_20260510_cli_commands Q12 specifies strategy variables "defaulting to `st.integers()`" — but the developer should at least know this happened. Silent fallback for domain-specific constraints (e.g., "parts must be >= 1") is a footgun. |
| PP6-Q3 | What is the gap? | `_resolve_placeholder()` in `decorators.py` falls back to `st.integers()` with no warning or logging. The developer has no visibility into which placeholders are using generic strategies vs. intentional ones. (Source: PM_20260511_strategy_fallback_confusing) |
| PP6-Q4 | Fix recommendation? | **Should.** Emit a `warnings.warn()` when `st.integers()` fallback is used — make the invisible visible. The warning should mention the placeholder name so developers know exactly what to fix. This is not a bug (the spec says `st.integers()` is the fallback) but it's a developer-experience improvement that prevents wasted debugging time. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Observability | When generate() runs, the output accurately reflects what was created and where | File paths in text output match actual created files (fixes PP1) | Must |
| QA2 | Code cleanliness | When generate() appends to an existing file, the result is idiomatic Python | One import block, no duplicates (fixes PP2) | Must |
| QA3 | Test integrity | When generated stubs are collected by pytest, they are clearly unimplemented | All stubs appear as SKIPPED, never PASSED (fixes PP4) | Must |
| QA4 | Feature completeness | When generate() creates a stub, it is wired to the .feature file's steps | Every stub has @Given/@When/@Then decorators matching .feature steps (fixes PP5) | Must |
| QA5 | Package correctness | When generate() creates a test directory, it is a proper Python package | `__init__.py` exists alongside every generated test file (fixes PP3) | Should |
| QA6 | Developer awareness | When strategy fallback is used, the developer is informed | A `UserWarning` identifies which placeholder fell back to `st.integers()` (fixes PP6) | Should |

---

## Pain Points Identified

- **PP1**: generate() text output shows empty file paths — key mismatch between `_process_scenario()` return dict and `_format_text_output()` read key. Developer cannot see what was created.
- **PP2**: generate() repeats import block per scenario when appending — each appended function re-emits all imports and strategy boilerplate. Multi-scenario features produce messy files.
- **PP3**: generate() creates directories without `__init__.py` — some pytest configurations fail to collect tests from non-package directories.
- **PP4**: generate() produces stubs that silently pass — `...` (Ellipsis) is a valid no-op, giving false confidence that unimplemented behavior is tested. Contradicts project's own `@pytest.mark.skip` + `raise NotImplementedError` convention.
- **PP5**: generate() omits step decorators — the core value proposition. `_parse_feature_steps()` exists but is disconnected from the generate flow, making decorator-producing code dead code.
- **PP6**: Strategy resolution silently falls back to `st.integers()` — for domain-specific constraints (e.g., "must be >= 1"), this produces `ZeroDivisionError` and confusing failures with no indication that the fallback was used.

## Business Goals Identified

- Make `generate()` produce stubs that are immediately useful — wired to .feature steps, clearly unimplemented, and structurally clean — so developers can start writing test bodies without manual setup
- Ensure generated code reflects the project's own conventions (skip markers, `__init__.py`, clean imports) — beehave must dogfood its own best practices
- Make invisible behavior visible — strategy fallback warnings help developers catch footguns before they waste time debugging surprising values

## Terms to Define (for glossary)

- **Strategy fallback** — When `_resolve_placeholder()` finds no module-level strategy variable and no @Example type inference for a `<placeholder>`, it defaults to `st.integers()`. This produces any integer, which may violate domain constraints.
- **Stub body convention** — The project's TDD convention for unimplemented test functions: `@pytest.mark.skip(reason="not yet implemented")` decorator + `raise NotImplementedError` body. Generated stubs must follow this convention.
- **Dead code path** — Code that is syntactically valid but never executed because its input is always empty. The step-decorator-producing code in `cli.py` (lines 199-215) is dead code because `_parse_feature_steps()` is disconnected from the generate flow.

## Action Items

- [ ] Fix PP1: Align dict keys between `_process_scenario()` and `_format_text_output()` — add text-mode output test
- [ ] Fix PP2: Add import-stripping to append path in `_append_function_stub()` or pass `is_append` flag — add multi-scenario append test
- [ ] Fix PP3: Add `__init__.py` creation to `_ensure_test_directory()` — add package structure test
- [ ] Fix PP4: Add `@pytest.mark.skip` + `raise NotImplementedError` to stub template — add test that generated stubs are SKIPPED by pytest
- [ ] Fix PP5: Connect `_parse_feature_steps()` to `_process_scenario()` — add test that generated stubs contain step decorators matching .feature steps
- [ ] Fix PP6: Add `warnings.warn()` to `_resolve_placeholder()` fallback path — add test that warning is emitted for unresolved placeholders
- [ ] Update IN_20260510_cli_commands Q12 to reflect stub body change: `raise NotImplementedError` instead of bare `...`, with `@pytest.mark.skip` decorator
- [ ] Prioritize fixes: PP5 (step decorators) and PP4 (skip markers) are highest value — they affect every generated stub's usability
