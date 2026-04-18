Feature: Test stub updates
  As a developer
  I want existing test stubs to be updated when the .feature file changes
  So that test stubs always reflect the current acceptance criteria

  Discovery:

  Status: BASELINED

  Entities:
  | Type | Name | Candidate Class/Method | In Scope |
  |------|------|----------------------|----------|
  | Noun | test stub | generated `test_<feature_slug>_<hex>()` method or function | Yes |
  | Noun | test file | `tests/features/<feature>/<rule_slug>_test.py` or `examples_test.py` | Yes |
  | Noun | feature slug | underscored folder name used in function names | Yes |
  | Noun | rule slug | `Rule:` title slugified; used as test file name | Yes |
  | Noun | class Test<RuleSlug> | class wrapping all stubs for a Rule block | Yes |
  | Noun | conforming test | test with correct file, correct class context, and correct function name | Yes |
  | Noun | non-conforming test | test whose `@id` exists in a feature file but is in the wrong file or class | Yes |
  | Noun | orphan test | test function with no matching `@id` in any `.feature` file | Yes |
  | Verb | update docstring | replace docstring to match current steps | Yes |
  | Verb | rename function | update function name if feature slug changed | Yes |
  | Verb | mark orphan | add `@pytest.mark.skip(reason="orphan: ...")` | Yes |
  | Verb | mark non-conforming | add `@pytest.mark.skip(reason="non-conforming: moved to <file>::<Class>")` | Yes |

  Rules (Business):
  - Only `backlog/` and `in-progress/` feature folders receive stub creation and updates
  - `completed/` features: only orphan detection runs (no creation, no docstring/name updates)
  - The docstring includes EVERY step line in order, including `And` and `But` continuations
  - Docstring format per step: `<Keyword>: <step text>` (e.g., `Given: user is logged in`, `And: user has admin role`)
  - Test function bodies are NEVER modified — parameter lists MAY be updated to stay in sync with documentation
  - stub-sync NEVER touches `@pytest.mark.slow` or any other software-engineer-owned marker
  - Conformance requires all three: (1) correct file (`<rule_slug>_test.py` or `examples_test.py`), (2) correct class context (`class Test<RuleSlug>` or module-level), (3) correct function name (`test_<feature_slug>_<8hex>`)
  - Non-conforming test (correct `@id`, wrong location or class): stub-sync creates a conforming version first, then marks the non-conforming test with `@pytest.mark.skip(reason="non-conforming: moved to <file>::<Class>")`
  - Orphaned tests (no matching `@id` in any `.feature` file) receive `@pytest.mark.skip(reason="orphan: no matching @id in .feature files")`

  Constraints:
  - Must never modify test function bodies
  - Must handle the case where a test file exists but is missing some stubs (add only the missing ones)
  - Function naming: `test_<feature_slug>_<id_hex>` — always, whether the stub is a method (inside a class) or a top-level function
  - stub-sync must not add or remove `@pytest.mark.slow`

  All questions answered. Discovery frozen.

  Architecture:

  ### Module Structure
  - `pytest_beehave/stub_reader.py` — `read_stubs_from_file(path) -> list[ExistingStub]`; `read_stubs_from_directory(directory) -> list[ExistingStub]`; `extract_example_id_from_name(function_name) -> ExampleId | None`. `ExistingStub` frozen dataclass (function_name, example_id, feature_slug, class_name, file_path, markers, docstring). `StubMarker` frozen dataclass (name, reason).
  - `pytest_beehave/stub_writer.py` — `mark_orphan(path, function_name) -> SyncAction`; `mark_non_conforming(path, function_name, correct_file, correct_class) -> SyncAction`; `toggle_deprecated_marker(path, function_name, *, should_be_deprecated) -> SyncAction`. Also `write_stub_to_file` for docstring/name updates.
  - `pytest_beehave/sync_engine.py` — orchestrates conformance check, orphan detection, non-conforming handling across all test files.

  ### Key Decisions
  ADR-001: Three-part conformance check
  Decision: A stub is conforming only if ALL THREE match: (1) correct file, (2) correct class context, (3) correct function name.
  Reason: Matches discovery.md conformance definition; partial matches are treated as non-conforming.
  Alternatives considered: Two-part check (file + name only) — rejected because class context is required per spec.

  ADR-002: Non-conforming handling creates conforming stub first, then marks original
  Decision: When a non-conforming stub is found, `sync_engine` first calls `write_stub_to_file` for the correct location, then calls `mark_non_conforming` on the original.
  Reason: Ensures traceability is never lost — the conforming stub exists before the original is marked.
  Alternatives considered: Delete the non-conforming stub — rejected because it loses the developer's implementation.

  ADR-003: stub_reader uses libcst to extract stub metadata
  Decision: `read_stubs_from_file` uses `libcst` to parse the test file and extract function names, decorators, and docstrings.
  Reason: Consistent with stub_writer's use of libcst; avoids dual-library complexity.
  Alternatives considered: `ast` module — rejected because it cannot extract decorator arguments reliably without round-trip capability.

  ADR-004: stub-sync never touches @pytest.mark.slow
  Decision: `toggle_deprecated_marker` and all other stub_writer functions check the marker name before modifying; `slow` is never added or removed.
  Reason: Matches marker ownership rules in discovery.md and AC `@id:c9a30d52`.
  Alternatives considered: Allowing stub-sync to manage all markers — rejected per spec.

  ### Build Changes (needs PO approval: yes)
  - New runtime dependency: `libcst>=1.0.0` — reason: read/write Python test files preserving formatting and comments (Q19 in discovery.md). Already added for stub-creation.

  Rule: Docstring updates
    As a developer
    I want existing test stubs to have their docstrings updated when the .feature file changes
    So that test stubs always reflect the current acceptance criteria wording

    @id:bdb8e233
    Example: Docstring is updated when step text changes
      Given an existing test stub whose docstring does not match the current step text in the .feature file
      When pytest is invoked
      Then the test stub docstring matches the current step text from the .feature file

    @id:6bb59874
    Example: Test body is not modified during docstring update
      Given an existing test stub with a custom implementation in the function body
      When pytest is invoked and the .feature file step text has changed
      Then the test function body below the docstring is unchanged

  Rule: Function renames
    As a developer
    I want test stubs to be renamed when the feature slug changes
    So that function names stay consistent with the feature folder

    @id:b6b9ab28
    Example: Function is renamed when the feature slug changes
      Given an existing test stub whose function name does not match the current feature slug
      When pytest is invoked
      Then the test function is renamed to match test_<current_feature_slug>_<id_hex>

    @id:d89540f9
    Example: Stubs in completed features are not updated
      Given a completed feature with a test stub whose docstring differs from the .feature file
      When pytest is invoked
      Then the completed feature test stub docstring is unchanged

  Rule: Non-conforming handling
    As a developer
    I want tests with a valid @id but in the wrong location to be redirected to the correct structure
    So that the canonical test layout is enforced without silently losing traceability

    @id:4a7c2e81
    Example: Non-conforming test receives redirect marker
      Given a test function whose @id matches a current Example but is in the wrong file or class
      When pytest is invoked
      Then stub-sync creates a conforming stub in the correct location and marks the original with @pytest.mark.skip(reason="non-conforming: moved to <file>::<Class>")

    @id:3f9d1b56
    Example: Once a conforming stub exists the non-conforming marker is preserved
      Given a non-conforming test already marked and a conforming stub already present in the correct location
      When pytest is invoked
      Then the non-conforming marker remains on the original test and the conforming stub is unchanged

  Rule: Orphan handling
    As a developer
    I want test functions with no matching @id in any .feature file to be marked as skipped
    So that stale tests do not pollute the test suite without being silently ignored

    @id:9d7a0b34
    Example: Orphan test receives skip marker
      Given a test file containing a test function whose @id hex does not match any Example in any .feature file
      When pytest is invoked
      Then that test function has @pytest.mark.skip(reason="orphan: no matching @id in .feature files") applied

    @id:67192894
    Example: Previously orphaned test loses skip marker when a matching Example is added
      Given a test function marked as orphan and a .feature file that now contains a matching @id Example
      When pytest is invoked
      Then the orphan skip marker is removed from that test function

    @id:8b2e4f17
    Example: Orphan detection runs on completed feature test files
      Given a completed feature test file containing a test function whose @id no longer exists in the feature file
      When pytest is invoked
      Then that test function receives @pytest.mark.skip(reason="orphan: no matching @id in .feature files")

    @id:c9a30d52
    Example: Stub-sync does not modify software-engineer-owned markers
      Given a test function with @pytest.mark.slow already applied by the software-engineer
      When pytest is invoked and stub-sync processes the feature
      Then @pytest.mark.slow is unchanged and no other software-engineer marker is added or removed
