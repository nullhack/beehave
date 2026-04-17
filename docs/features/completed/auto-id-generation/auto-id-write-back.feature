Feature: Auto ID write-back
  As a developer
  I want Examples without an @id tag to receive a generated ID written back to the .feature file
  So that every Example is uniquely identified without manual intervention

  @id:cd98877d
  Example: Untagged Example receives a generated @id tag
    Given a writable .feature file containing an Example with no @id tag
    When pytest is invoked
    Then the .feature file contains an @id:<8-char-hex> tag on the line immediately before that Example

  @deprecated @id:09a986e7
  Example: Generated ID is globally unique across all feature files
    Given a project with multiple .feature files each containing untagged Examples
    When pytest is invoked
    Then each generated @id tag is unique across all .feature files in the project

  @id:27cf14bf
  Example: Generated IDs are unique within the feature file being processed
    Given a writable .feature file containing multiple untagged Examples
    When pytest is invoked
    Then all generated @id tags within that file are unique

  @id:842409ed
  Example: Tagged Examples are not modified
    Given a .feature file where all Examples already have @id tags
    When pytest is invoked
    Then the .feature file content is unchanged
