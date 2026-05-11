Feature: Generate Messaging

  The beehave generate command must distinguish between "no scenarios exist in the file" and "scenarios exist but lack @id tags" and provide actionable guidance for the latter case. When generate encounters scenarios without @id tags, it must inform the developer to run sync first — it must not silently skip with a misleading "no scenarios found" message and must not auto-invoke sync.

  Rules (Business):
  - When generate encounters scenarios without @id tags, it must produce an actionable message advising the developer to run sync first
  - When generate encounters a .feature file with zero scenarios, it must report "no scenarios found" (distinct from "scenarios exist without @id tags")
  - When generate encounters N scenarios where all lack @id tags, it must report "N scenarios found without @id tags. Run 'beehave sync' first, then re-run generate."
  - generate() must not auto-invoke sync() — the two commands have separate responsibilities and separate side effects (generate writes to tests/, sync mutates .feature files)
  - The developer can distinguish "nothing to do" from "you need to take an action" based on generate's output message
  - GenerateStub can only create stubs for scenarios with assigned @id tags — scenarios without @id are a precondition failure, not a "no data" condition

  Constraints:
  - Developer guidance (QA11): when generate() is run on untagged scenarios, the developer is told what to do; output says "N scenarios found without @id tags — run sync first"
  - generate() must not auto-invoke sync() — advise only (architecture decision AD3: single-responsibility, composability over magic)
  - Idempotency: running generate multiple times with the same input produces the same output and same guidance
  - Safety: generate is additive-only and never modifies .feature files
  - MoSCoW: Should

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP11 — generate() silently skips scenarios without @id tags with misleading "no scenarios found" message |
