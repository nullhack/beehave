Feature: sync-create — generate new test stubs for new Examples

  Generates a skipped test stub function for each Example in a .feature file that has no
  corresponding test identified by its @id. The stub carries the full Gherkin step text as its
  docstring, uses the active adapter's skip marker and body convention, and is placed in
  tests/features/<feature_slug>/<rule_slug>_test.py.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - A stub is created only when no test function with the @id in its name already exists
  - One test file is created per Rule block: tests/features/<feature_slug>/<rule_slug>_test.py

  Constraints:
  - Function name: test_<feature_slug>_<id>
  - Docstring: full Gherkin step text verbatim (all Given/When/Then lines)
  - Return type: -> None; body: ... (Ellipsis)
  - Skip marker and body come from the active adapter template

  Rule: Stub creation
    As a developer
    I want beehave sync to generate a test stub for each new Example
    So that every acceptance criterion is represented in my test suite immediately

    @id:c8911ca5
    Example: New Example produces a skipped stub function
      Given a .feature file with an Example tagged @id:a1b2c3d4 and no corresponding test function
      When beehave sync runs
      Then a function named test_<feature_slug>_a1b2c3d4 exists in the correct test file, decorated with the adapter's skip marker

    @id:08a9661d
    Example: Existing stub is not recreated
      Given a test function test_<feature_slug>_a1b2c3d4 already exists
      When beehave sync runs
      Then the existing function is not modified and no duplicate is created

    @id:3941f0ca
    Example: Stub docstring contains all Given/When/Then lines verbatim
      Given an Example with three Gherkin steps
      When beehave sync generates the stub
      Then the function docstring contains all three step lines exactly as they appear in the .feature file

  Rule: Test file layout
    As a developer
    I want each Rule's stubs to be in their own file under the feature slug directory
    So that test files are small and map directly to user stories

    @id:b8483d50
    Example: Test file is created at the correct path
      Given a .feature file with slug "honey-flow" and a Rule with slug "nectar-collection"
      When beehave sync creates the stub
      Then the stub is placed in tests/features/honey_flow/nectar_collection_test.py

    @id:23de0b22
    Example: Missing parent directories are created
      Given tests/features/honey_flow/ does not exist
      When beehave sync creates a stub for the honey-flow feature
      Then tests/features/honey_flow/ is created along with the stub file

    @id:b6927bfd
    Example: Multiple Rules in one feature produce separate test files
      Given a .feature file with two Rule blocks
      When beehave sync runs
      Then two test files are created, one per Rule, under tests/features/<feature_slug>/

  Rule: Idempotency
    As a developer
    I want beehave sync to be safe to run multiple times
    So that I can run it in CI without risk of duplicate stubs

    @id:23af2d01
    Example: Running sync twice does not produce duplicate functions
      Given beehave sync has already been run for a feature
      When beehave sync is run again without changes to the .feature file
      Then the test files are unchanged
