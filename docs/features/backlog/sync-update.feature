Feature: sync-update — update existing stubs when .feature content changes

  Updates the metadata of existing test stub functions when their corresponding Example changes
  in the .feature file. Specifically: the docstring is re-rendered to match new step text, the
  function name is updated if the feature slug changed, and the @deprecated marker is toggled
  based on the Gherkin @deprecated tag. beehave never modifies a test body under any circumstance.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - Test bodies are never modified under any circumstance
  - Scenario Outline column changes are warned about and never auto-modified

  Constraints:
  - @deprecated marker is added or removed based solely on the Gherkin @deprecated tag presence
  - Function rename on slug change preserves the test body exactly

  Rule: Docstring update
    As a developer
    I want beehave to keep my stub docstrings in sync with the .feature file
    So that the living documentation in my test file stays accurate

    @id:ec1cd20f
    Example: Changed step text updates the stub docstring
      Given an Example whose Given/When/Then steps have changed in the .feature file
      When beehave sync runs
      Then the corresponding stub function's docstring reflects the new step text

    @id:0e8f0c8a
    Example: Unchanged step text leaves the stub docstring untouched
      Given an Example whose steps have not changed since the last sync
      When beehave sync runs
      Then the stub function's docstring is unchanged

  Rule: Body preservation
    As a developer
    I want beehave to never touch my test body under any circumstances
    So that I can trust beehave will not break my implemented tests

    @id:37751b69
    Example: Implemented test body is preserved when docstring updates
      Given a stub whose body has been implemented by a developer
      When the corresponding Example's step text changes and beehave sync runs
      Then the docstring is updated and the body is byte-for-byte unchanged

    @id:d978b45d
    Example: Skipped stub body is preserved when docstring updates
      Given a stub with body ... (Ellipsis) and an updated Example
      When beehave sync runs
      Then the body remains ... and only the docstring changes

  Rule: Deprecated marker sync
    As a developer
    I want beehave to add or remove the deprecated marker based on the @deprecated Gherkin tag
    So that my test suite reflects which acceptance criteria are no longer active

    @id:2fd7a849
    Example: @deprecated tag on Example adds deprecated marker to stub
      Given an Example without @deprecated that gains a @deprecated tag in the .feature file
      When beehave sync runs
      Then the stub function gains the adapter's deprecated marker decorator

    @id:13c1267d
    Example: Removing @deprecated tag removes deprecated marker from stub
      Given a stub with the deprecated marker whose @deprecated tag is removed from the .feature file
      When beehave sync runs
      Then the deprecated marker decorator is removed from the stub function

  Rule: Scenario Outline column change warning
    As a developer
    I want beehave to warn me when Scenario Outline columns change
    So that I know to manually update the parametrize decorator myself

    @id:2d128d78
    Example: Column change in Examples table produces a warning
      Given a Scenario Outline stub whose Examples table columns have changed
      When beehave sync runs
      Then beehave emits a warning identifying the affected stub and does not modify the parametrize decorator
