Feature: Test stub update
  As a developer
  I want existing test stubs to have their names and docstrings updated when the .feature file changes
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
