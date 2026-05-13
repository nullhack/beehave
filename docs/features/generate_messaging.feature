Feature: Generate Messaging

  The beehave generate command must distinguish between "no scenarios exist in the file" and "scenarios exist but lack @id tags" and provide actionable guidance for the latter case. When generate encounters scenarios without @id tags, it must inform the developer to run sync first — it must not silently skip with a misleading "no scenarios found" message and must not auto-invoke sync.

  Constraints:
  - Developer guidance (QA11): when generate() is run on untagged scenarios, the developer is told what to do; output says "N scenarios found without @id tags — run sync first"
  - generate() must not auto-invoke sync() — advise only (architecture decision AD3: single-responsibility, composability over magic)
  - GenerateStub can only create stubs for scenarios with assigned @id tags — scenarios without @id are a precondition failure, not a "no data" condition
  - Idempotency: running generate multiple times with the same input produces the same output and same guidance
  - Safety: generate is additive-only and never modifies .feature files
  - MoSCoW: Should

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP11 — generate() silently skips scenarios without @id tags with misleading "no scenarios found" message |
  | 2026-05-11 | Break-down: 2 Rules (untagged advisory + empty file distinction), 3 Examples (all-untagged, partial-untagged, empty-file) |

  Rule: Advisory for scenarios without @id tags
    As a developer running `beehave generate`
    I want to be informed when scenarios in my .feature file lack @id tags, with a count and advice to run sync
    So that I know what action to take instead of seeing a misleading "no scenarios found" message

    @id:7a3f9b2e
    Example: All scenarios lack @id tags — advisory message with count, no stubs created
      Given a .feature file containing 3 scenarios, none with @id tags
      When the developer runs `beehave generate` for that feature
      Then the output contains "3 scenarios found without @id tags"
      And the output contains "Run 'beehave sync' first"
      And no test stubs are created
      And no .feature files are modified

    @id:8c4d0e6f
    Example: Some scenarios lack @id tags — stubs for tagged ones, warning about untagged count
      Given a .feature file containing 5 scenarios where 3 have @id tags and 2 do not
      When the developer runs `beehave generate` for that feature
      Then test stubs are created for the 3 tagged scenarios
      And the output contains "2 scenarios found without @id tags"
      And the output contains "Run 'beehave sync' first"
      And no .feature files are modified

  Rule: Empty feature file produces distinct message
    As a developer running `beehave generate`
    I want a "no scenarios found" message only when my .feature file truly contains no scenarios
    So that I can distinguish a genuinely empty file from one that needs sync

    @id:2b5e1a9c
    Example: Feature file with zero scenarios — distinct "no scenarios found" message
      Given a .feature file containing 0 scenarios
      When the developer runs `beehave generate` for that feature
      Then the output contains "no scenarios found"
      And the output does NOT contain "without @id tags"
      And no test stubs are created
