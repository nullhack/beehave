Feature: Auto ID generation and enforcement
  Ensures every Example in a .feature file has a unique @id tag. When an untagged Example is found
  in a writable environment, an ID is generated and written back in-place. In a read-only environment
  (CI), the pytest run fails with a descriptive error naming the untagged Example.

  Status: BASELINED (2026-04-18)

  Rules (Business):
  - Every `Example:` block MUST have an `@id:<8-char-hex>` tag before the stub sync proceeds
  - If any Example lacks an `@id` tag AND the `.feature` file is writable, generate an ID and write it back in-place, then continue
  - If any Example lacks an `@id` tag AND the `.feature` file is NOT writable (CI / read-only), fail the pytest run with a descriptive error: "Untagged Examples found — run pytest locally to generate IDs"
  - Generated IDs are 8-character lowercase hexadecimal strings, unique within the feature file being processed
  - IDs are written on the line immediately before the `Example:` keyword

  Constraints:
  - Must not corrupt the `.feature` file — only insert the `@id` tag line, leave all other content unchanged
  - Must detect read-only filesystem before attempting write (check file writability, not just `CI` env var)
  - The error message must name the specific `.feature` file(s) and Example title(s) that are missing IDs

  Rule: Auto ID write-back
    As a developer
    I want Examples without an @id tag to receive a generated ID written back to the .feature file
    So that every Example is uniquely identified without manual intervention

    @id:cd98877d
    Example: Untagged Example receives a generated @id tag
      Given a writable .feature file containing an Example with no @id tag
      When pytest is invoked
      Then the .feature file contains an @id:<8-char-hex> tag on the line immediately before that Example

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

    @bug
    @id:a7b5c493
    Example: Existing non-hex @id is used as-is for stub naming and no new @id is added
      Given a writable .feature file containing an Example tagged @id:my-custom-name (non-hex format)
      When pytest is invoked
      Then the generated stub function is named test_<feature_slug>_my-custom-name and no additional @id tag is written to the .feature file

    @bug
    @id:b8c6d504
    Example: Two @id tags on one Example cause a hard error at startup
      Given a .feature file containing an Example with two @id tags on separate lines before the Example keyword
      When pytest is invoked
      Then pytest exits with a non-zero status code and an error message naming the Example with duplicate @id tags

    @bug
    @id:e9d7f615
    Example: Non-8-char @id tag is included in the uniqueness set so generated IDs never collide with it
      Given a writable .feature file containing an Example tagged @id:abcdef012 (9 hex chars, not 8)
      When pytest is invoked
      Then no new @id tag is written to the .feature file
      And the existing @id:abcdef012 tag is preserved unchanged
      And any other generated IDs in the same file do not share their first 8 characters with abcdef012

  Rule: CI ID enforcement
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
