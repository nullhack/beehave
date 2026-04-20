Feature: Test stub updates
  Updates existing test stubs when a .feature file changes: refreshes docstrings, renames functions
  when the feature slug changes, marks non-conforming stubs, and marks orphaned stubs. Completed
  features receive only orphan detection.

  Status: BASELINED (2026-04-18)

  Rules (Business):
  - Only `backlog/` and `in-progress/` feature folders receive stub creation and updates
  - `completed/` features: only orphan detection runs (no creation, no docstring/name updates)
  - The docstring includes EVERY step line in order, including `And` and `But` continuations
  - Docstring format per step: `<Keyword>: <step text>` (e.g., `Given: user is logged in`, `And: user has admin role`)
  - Test function bodies are NEVER modified — parameter lists MAY be updated to stay in sync with documentation
  - stub-sync NEVER touches `@pytest.mark.slow` or any other software-engineer-owned marker
  - Conformance requires both: (1) correct file (`<rule_slug>_test.py` or `examples_test.py`), (2) correct function name (`test_<feature_slug>_<@id>`)
  - Non-conforming test (correct `@id`, wrong file): stub-sync creates a conforming version first, then marks the non-conforming test with `@pytest.mark.skip(reason="non-conforming: moved to <file>")`
  - Orphaned tests (no matching `@id` in any `.feature` file) receive `@pytest.mark.skip(reason="orphan: no matching @id in .feature files")`

  Constraints:
  - Must never modify test function bodies
  - Must handle the case where a test file exists but is missing some stubs (add only the missing ones)
  - Function naming: `test_<feature_slug>_<@id>` — always a top-level function
  - stub-sync must not add or remove `@pytest.mark.slow`

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

    @bug
    @id:d6a4f382
    Example: Background steps are separated from scenario steps by a blank line when docstring is updated
      Given an existing test stub for a feature with a Background section whose docstring does not have a blank line between Background steps and Scenario steps
      When pytest is invoked and the stub docstring is updated
      Then the updated docstring contains a blank line between the last Background step and the first Scenario step

  Rule: Function renames
    As a developer
    I want test stubs to be renamed when the feature slug changes
    So that function names stay consistent with the feature folder

    @id:b6b9ab28
    Example: Function is renamed when the feature slug changes
      Given an existing test stub whose function name does not match the current feature slug
      When pytest is invoked
      Then the test function is renamed to match test_<current_feature_slug>_<@id>

    @id:d89540f9
    Example: Stubs in completed features are not updated
      Given a completed feature with a test stub whose docstring differs from the .feature file
      When pytest is invoked
      Then the completed feature test stub docstring is unchanged

  Rule: Non-conforming handling
    As a developer
    I want tests with a valid @id but in the wrong location to be redirected to the correct structure
    So that the canonical test layout is enforced without silently losing traceability

    @deprecated
    @id:4a7c2e81
    Example: Non-conforming test receives redirect marker
      Given a test function whose @id matches a current Example but is in the wrong file or class
      When pytest is invoked
      Then stub-sync creates a conforming stub in the correct location and marks the original with @pytest.mark.skip(reason="non-conforming: moved to <file>::<Class>")

    @id:7e1a3c90
    Example: Non-conforming test receives redirect marker
      Given a test function whose @id matches a current Example but is in the wrong file
      When pytest is invoked
      Then stub-sync creates a conforming stub in the correct location and marks the original with @pytest.mark.skip(reason="non-conforming: moved to <file>")

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
