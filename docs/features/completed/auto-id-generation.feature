Feature: Auto ID generation and enforcement
  As a developer
  I want Examples without an @id tag to receive a generated ID written back to the .feature file (or fail in CI)
  So that every Example is uniquely identified without manual intervention

  Discovery:

  Status: BASELINED

  Entities:
  | Type | Name | Candidate Class/Method | In Scope |
  |------|------|----------------------|----------|
  | Noun | Example block | Gherkin scenario | Yes |
  | Noun | `@id` tag | `@id:<8-char-hex>` tag on Example | Yes |
  | Noun | `.feature` file | Gherkin feature file on disk | Yes |
  | Noun | hex ID | 8-character lowercase hex string | Yes |
  | Noun | CI environment | read-only or automated environment | Yes |
  | Verb | detect missing ID | scan Example tags for `@id` | Yes |
  | Verb | generate ID | produce a unique 8-char hex string | Yes |
  | Verb | write back | insert `@id` tag into `.feature` file in-place | Yes |
  | Verb | fail run | abort pytest with a clear error message | Yes |

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

  Questions:
  | ID | Question | Answer | Status |
  |----|----------|--------|--------|
  | Q1 | Should ID uniqueness be guaranteed globally (across all feature files) or just within a single file? | Within-file only — scan the current `.feature` file for existing `@id` values before generating new ones for that file; 8-char hex collision probability across files is negligible | ANSWERED (REVISED) |
  | Q2 | How is "CI / read-only" detected — by checking file writability or by checking a `CI` env var? | Check file writability — more reliable across different CI systems | ANSWERED |

  All questions answered. Discovery frozen.

  Architecture:

  ### Module Structure
  - `pytest_beehave/id_generator.py` — `generate_unique_id(existing_ids: set[ExampleId]) -> ExampleId`; `find_untagged_examples(feature_text: str) -> list[UntaggedExample]`; `write_back_ids(path, filesystem) -> IdWriteBackResult`. `FileSystemProtocol` Protocol. `UntaggedExample` frozen dataclass (title, line_number). `IdWriteBackResult` frozen dataclass (path, assigned dict, skipped list).
  - `pytest_beehave/models.py` — `ExampleId` frozen dataclass (value: str) — shared with stub_writer, stub_reader, feature_parser.

  ### Key Decisions
  ADR-001: Detect read-only by checking file writability, not CI env var
  Decision: Use `os.access(path, os.W_OK)` via `FileSystemProtocol.is_writable` to determine if write-back is possible.
  Reason: More reliable across different CI systems than checking `CI` env var; matches AC Q2 answer.
  Alternatives considered: Checking `os.environ.get("CI")` — rejected per AC Q2.

  ADR-002: ID uniqueness is within-file only
  Decision: `generate_unique_id` takes `existing_ids: set[ExampleId]` scanned from the current file only.
  Reason: Matches AC Q1 answer; cross-file collision probability with 8-char hex is negligible.
  Alternatives considered: Global uniqueness across all feature files — rejected per AC Q1.

  ADR-003: Write @id tag on the line immediately before the Example keyword
  Decision: Insert the `@id:<hex>` tag line immediately before the `Example:` keyword line.
  Reason: Matches the Gherkin tag convention and AC requirement.
  Alternatives considered: Appending to existing tag lines — rejected because it may break gherkin-official parsing.

  ### Build Changes (needs PO approval: no)
  - No new runtime dependencies (uses stdlib `os`, `uuid`, and `re`).

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