Feature: ID Generation — assign @id tags to untagged Examples
Status: BASELINED (2026-04-23)

Beehave assigns unique 8-character lowercase hex `@id` tags to Gherkin
Examples that lack them. Existing valid IDs are never overwritten.
Malformed `@id` tags are treated as missing and replaced.

Rule: Beehave generates IDs for untagged Examples

  @id:f888a23f
  Example: Untagged Example receives a new @id
    Given a `.feature` file with an Example that has no `@id` tag
    When beehave assigns IDs
    Then the Example receives an `@id:<8-char-hex>` tag
    And the tag is a valid 8-character lowercase hex string

  @id:ec32fe63
  Example: Multiple untagged Examples each get unique IDs
    Given a `.feature` file with three Examples without `@id` tags
    When beehave assigns IDs
    Then each Example receives a distinct `@id` tag

Rule: Existing valid IDs are preserved

  @id:d2e63026
  Example: Developer-supplied ID is left untouched
    Given a `.feature` file with an Example tagged `@id:custom01`
    When beehave assigns IDs
    Then the `@id:custom01` tag is preserved as-is

  @id:8499105f
  Example: Valid hex ID is never regenerated
    Given a `.feature` file with an Example tagged `@id:a1b2c3d4`
    When beehave assigns IDs
    Then the `@id:a1b2c3d4` tag is left unchanged

Rule: Malformed IDs are replaced

  @id:4282d12b
  Example: Empty @id is replaced
    Given a `.feature` file with an Example tagged `@id:`
    When beehave assigns IDs
    Then the malformed tag is replaced with a new valid `@id`

  @id:553b3cf7
  Example: Non-hex @id is replaced
    Given a `.feature` file with an Example tagged `@id:ZZZZZZZZ`
    When beehave assigns IDs
    Then the malformed tag is replaced with a new valid `@id`

Rule: ID uniqueness is project-wide

  @id:12a7a112
  Example: Duplicate @id across files triggers warning or error
    Given two `.feature` files each containing `@id:a1b2c3d4`
    When beehave assigns IDs
    Then a warning or error is raised depending on configuration

  @id:9ecaf8b1
  Example: Collision on generation is silently retried
    Given a randomly generated ID that already exists in the project
    When beehave assigns IDs
    Then a new random ID is generated until unique

Rule: Write-back preserves formatting

  @id:b491f526
  Example: Only the @id tag line is modified
    Given a `.feature` file with specific whitespace and formatting
    When beehave assigns IDs
    Then all whitespace and formatting is preserved except for the added `@id` tag

Rule: Python API is available

  @id:e23fa86f
  Example: Programmatic ID assignment
    Given a project with untagged Examples
    When the developer calls `from beehave import assign_ids`
    Then IDs are assigned the same way as the CLI
