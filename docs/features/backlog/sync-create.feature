Feature: sync-create — generate new test stubs for new Examples

  Generates a skipped test stub function for each Example in a .feature file that has no
  corresponding test identified by its @id. The stub carries the full Gherkin step text as its
  docstring, uses the active adapter's skip marker and body convention, and is placed in
  tests/features/<feature_slug>/<rule_slug>_test.py.

  Status: ELICITING

  Rules (Business):
  - A stub is created only when no test function with the @id in its name already exists
  - One test file is created per Rule block: tests/features/<feature_slug>/<rule_slug>_test.py

  Constraints:
  - Function name: test_<feature_slug>_<id>
  - Docstring: full Gherkin step text verbatim (all Given/When/Then lines)
  - Return type: -> None; body: ... (Ellipsis)
  - Skip marker and body come from the active adapter template
