Feature: sync-update — update existing stubs when .feature content changes

  Updates the metadata of existing test stub functions when their corresponding Example changes
  in the .feature file. Specifically: the docstring is re-rendered to match new step text, the
  function name is updated if the feature slug changed, and the @deprecated marker is toggled
  based on the Gherkin @deprecated tag. beehave never modifies a test body under any circumstance.

  Status: ELICITING

  Rules (Business):
  - Test bodies are never modified under any circumstance
  - Scenario Outline column changes are warned about and never auto-modified

  Constraints:
  - @deprecated marker is added or removed based solely on the Gherkin @deprecated tag presence
  - Function rename on slug change preserves the test body exactly
