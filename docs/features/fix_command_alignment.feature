Feature: Fix Command Alignment

  The beehave fix command must use content-based diff alignment (not positional comparison) to accurately match .feature steps to existing test decorators. When a developer inserts a new step mid-scenario, fix must propose a single insertion — not a cascade of N text replacements. This replaces the positional comparison in _find_text_mismatches() with difflib.SequenceMatcher.

  Rules (Business):
  - When a step is inserted mid-scenario, fix proposes a single insertion rather than N replacements
  - When a step is deleted, fix proposes a single deletion rather than N replacements
  - When step text has changed (not just shifted), fix classifies the mismatch as a replace
  - Content-based matching does not falsely align steps with similar but different text
  - Fix results are idempotent — applying changes then running fix again reports no mismatches

  Constraints:
  - Fix accuracy (QA10): when a step is inserted mid-scenario, fix proposes a single insertion; fix --dry-run shows 1 insertion, not N replacements
  - Idempotency: running fix multiple times produces the same result — once changes are applied, a subsequent fix reports no mismatches
  - Safety: fix --dry-run shows changes without modifying files; fix without --dry-run modifies files after confirmation
  - Architecture decision AD2: use difflib.SequenceMatcher (stdlib) with autojunk=False; get_opcodes() classifies equal/replace/insert/delete
  - SequenceMatcher is O(n²) worst case but typical step counts are under 20 — performance is negligible
  - MoSCoW: Should

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP10 — fix step insertion misalignment from positional comparison |
  | 2026-05-11 | Break-down: consolidated 7 coarse rules into 3 Rule blocks with 5 Examples |

  Rule: Diff-based alignment correctly identifies insertions and deletions
    As a developer
    I want fix to propose a single change when a step is inserted or deleted mid-scenario
    So that I see the actual number of changes needed, not a cascade of text replacements

    @id:a1c3e5f7
    Example: Step inserted mid-scenario produces a single insertion proposal
      Given a .feature scenario with steps "Given setup" "Then verify"
      And a test with decorators @Given("setup") @Then("verify")
      When the developer inserts "When action" between setup and verify in the .feature file
      And runs beehave fix --dry-run
      Then fix proposes 1 insertion for "When action"
      And does not propose any text replacements for existing decorators

    @id:b2d4f6a8
    Example: Step deleted from mid-scenario produces a single deletion proposal
      Given a .feature scenario with steps "Given setup" "When action" "Then verify"
      And a test with decorators @Given("setup") @When("action") @Then("verify")
      When the developer removes "When action" from the .feature file
      And runs beehave fix --dry-run
      Then fix proposes 1 deletion for @When("action")
      And does not propose any text replacements for the remaining decorators

  Rule: Diff-based alignment distinguishes text changes from positional shifts
    As a developer
    I want fix to correctly identify when step text has changed versus when steps have shifted position
    So that content-based matching does not falsely align different step texts

    @id:c3e5a7b1
    Example: Changed step text is classified as replace, not insert plus delete
      Given a .feature scenario with step "When the user deposits <amount>"
      And a test with decorator @When("the user withdraws <amount>")
      When beehave fix compares the feature steps to test decorators
      Then fix classifies the mismatch as a single replace operation
      And the mismatch carries expected "the user deposits <amount>" and actual "the user withdraws <amount>"

    @id:d4f6b8c2
    Example: Steps with similar text are not falsely aligned
      Given a .feature scenario with steps "Given a user exists" "Given a user is admin"
      And a test with decorators @Given("a user exists") @Given("a user is admin")
      When the developer inserts "When the user logs in" between them in the .feature file
      And runs beehave fix --dry-run
      Then fix proposes 1 insertion for "When the user logs in"
      And does not propose text replacements for the existing similar decorators

  Rule: Fix alignment results are idempotent
    As a developer
    I want fix to produce stable results across multiple runs
    So that I can trust the change proposals are complete and accurate

    @id:e5a7c9d3
    Example: Running fix after applying changes reports no mismatches
      Given a .feature scenario with 3 steps and a test with 2 matching decorators and 1 mismatched decorator
      When the developer runs beehave fix and applies all proposed changes
      And then runs beehave fix again
      Then fix reports no mismatches
