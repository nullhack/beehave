Feature: Deprecation marker sync
  As a developer
  I want @pytest.mark.deprecated to be toggled on test functions whenever the @deprecated tag changes in the .feature file
  So that deprecated acceptance criteria are automatically skipped across all feature stages

  Discovery:

  Status: BASELINED

  Entities:
  | Type | Name | Candidate Class/Method | In Scope |
  |------|------|----------------------|----------|
  | Noun | `@deprecated` tag | Gherkin tag directly on an Example block | Yes |
  | Noun | Gherkin tag inheritance | `@deprecated` on a `Rule:` or `Feature:` node applies to all child Examples | Yes |
  | Noun | `@pytest.mark.deprecated` | pytest marker on a test function | Yes |
  | Noun | backlog stage | `docs/features/backlog/` | Yes |
  | Noun | in-progress stage | `docs/features/in-progress/` | Yes |
  | Noun | completed stage | `docs/features/completed/` | Yes |
  | Verb | detect deprecated | check Example tags for `@deprecated` (direct and inherited) | Yes |
  | Verb | add marker | prepend `@pytest.mark.deprecated` to test function | Yes |
  | Verb | remove marker | remove `@pytest.mark.deprecated` when tag is gone | Yes |

  Rules (Business):
  - ALL 3 feature stages (backlog, in-progress, completed) are checked for `@deprecated` tag changes
  - Gherkin tag inheritance applies: `@deprecated` on a `Rule:` or `Feature:` node is treated as present on all child Examples
  - If an Example has `@deprecated` tag (directly or via inheritance) and the test function lacks `@pytest.mark.deprecated`, add the marker
  - If an Example no longer has `@deprecated` tag (directly or via inheritance) and the test function has `@pytest.mark.deprecated`, remove the marker
  - Deprecation sync never modifies test function bodies or parameter lists
  - Deprecation sync is the ONLY operation performed on `completed/` feature test files

  Constraints:
  - Must handle the case where the test function does not exist (skip — stub sync handles creation)
  - Must not add duplicate `@pytest.mark.deprecated` markers

  Questions:
  | ID | Question | Answer | Status |
  |----|----------|--------|--------|
  | Q1 | Should deprecation sync run even if stub sync is skipped for completed features? | Yes — deprecation sync always runs on all 3 stages regardless | ANSWERED |

  All questions answered. Discovery frozen.

  Architecture:

  ### Module Structure
  - `pytest_beehave/feature_parser.py` — `ParsedExample.is_deprecated` (bool, resolved including inheritance from Rule and Feature nodes); `ParsedRule.is_deprecated`; `ParsedFeature.is_deprecated`. Tag inheritance is resolved inside `parse_feature` so callers see a flat flag.
  - `pytest_beehave/stub_writer.py` — `toggle_deprecated_marker(path, function_name, *, should_be_deprecated) -> SyncAction`. Adds `@pytest.mark.deprecated` when True, removes it when False, no-op if already in correct state.
  - `pytest_beehave/sync_engine.py` — deprecation sync runs on ALL 3 stages (backlog, in-progress, completed); calls `toggle_deprecated_marker` for each Example whose stub exists.

  ### Key Decisions
  ADR-001: Tag inheritance resolved at parse time, not at sync time
  Decision: `parse_feature` resolves `@deprecated` inheritance (Feature → Rule → Example) and sets `ParsedExample.is_deprecated` as a flat bool.
  Reason: Keeps sync_engine simple — it only reads `example.is_deprecated`; no inheritance logic scattered across modules.
  Alternatives considered: Resolving inheritance in sync_engine — rejected because it duplicates logic and couples sync_engine to Gherkin tag semantics.

  ADR-002: Deprecation sync runs on completed/ features
  Decision: `run_sync` calls deprecation sync for all three stages, including completed/.
  Reason: Matches AC `@id:fc372f15` and discovery.md rule: "Deprecation sync is the ONLY operation performed on completed/ feature test files."
  Alternatives considered: Skipping completed/ for deprecation sync — rejected per spec.

  ADR-003: No duplicate @pytest.mark.deprecated markers
  Decision: `toggle_deprecated_marker` reads existing markers via `stub_reader` before writing; skips if already in correct state.
  Reason: Matches constraint "Must not add duplicate @pytest.mark.deprecated markers".
  Alternatives considered: Always removing then re-adding — rejected because it causes unnecessary file writes.

  ### Build Changes (needs PO approval: yes)
  - New runtime dependency: `libcst>=1.0.0` — reason: read/write Python test files preserving formatting and comments. Already added for stub-creation.

  Rule: Mark deprecated Examples
    As a developer
    I want @pytest.mark.deprecated to be toggled on test functions whenever the @deprecated tag changes in the .feature file
    So that deprecated acceptance criteria are automatically skipped across all feature stages

    @id:f9b636df
    Example: Deprecated Example in a backlog feature gets the deprecated marker
      Given a backlog feature with an Example tagged @deprecated whose test stub lacks @pytest.mark.deprecated
      When pytest is invoked
      Then the test stub has @pytest.mark.deprecated applied

    @id:fc372f15
    Example: Deprecated Example in a completed feature gets the deprecated marker
      Given a completed feature with an Example tagged @deprecated whose test stub lacks @pytest.mark.deprecated
      When pytest is invoked
      Then the test stub has @pytest.mark.deprecated applied

  Rule: Mark deprecated via tag inheritance
    As a developer
    I want @pytest.mark.deprecated applied to all child Examples when @deprecated is on a Rule or Feature
    So that deprecating an entire rule or feature is a single tag change

    @id:b3d7f942
    Example: @deprecated on a Rule block propagates to all child Examples
      Given a backlog feature with a Rule tagged @deprecated containing multiple Examples
      When pytest is invoked
      Then all test stubs for Examples in that Rule have @pytest.mark.deprecated applied

    @id:a9e1c504
    Example: @deprecated on the Feature node propagates to all Examples in the feature
      Given a backlog feature tagged @deprecated at the Feature level containing multiple Rules and Examples
      When pytest is invoked
      Then all test stubs for all Examples in that feature have @pytest.mark.deprecated applied

    @id:d6f8b231
    Example: Removing @deprecated from a Rule removes the marker from all child stubs
      Given a Rule whose @deprecated tag has been removed but whose child test stubs all have @pytest.mark.deprecated
      When pytest is invoked
      Then @pytest.mark.deprecated is removed from all child test stubs of that Rule

  Rule: Remove deprecated marker
    As a developer
    I want @pytest.mark.deprecated removed when the @deprecated tag is removed from an Example
    So that tests are not skipped when acceptance criteria are no longer deprecated

    @id:7fcee92a
    Example: Deprecated marker is removed when @deprecated tag is removed
      Given a feature with an Example that no longer has the @deprecated tag but whose test stub has @pytest.mark.deprecated
      When pytest is invoked
      Then @pytest.mark.deprecated is removed from that test stub