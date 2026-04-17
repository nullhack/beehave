Feature: CI ID enforcement
  As a CI pipeline
  I want pytest to fail when untagged Examples are found in a read-only environment
  So that developers are forced to generate IDs locally before pushing

  @id:c4d6d9ce
  Example: pytest fails when untagged Examples exist in a read-only feature file
    Given a read-only .feature file containing an Example with no @id tag
    When pytest is invoked
    Then the pytest run exits with a non-zero status code

  @id:8b9230d4
  Example: Error message names the file and Example title
    Given a read-only .feature file containing an Example with no @id tag
    When pytest is invoked
    Then the error output names the .feature file path and the Example title that is missing an @id
