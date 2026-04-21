Feature: Deprecation marker sync
  Keeps @pytest.mark.deprecated in sync with the @deprecated Gherkin tag across all three feature
  stages. Adds the marker when the tag appears (including via Rule or Feature-level inheritance) and
  removes it when the tag is gone. Completed features receive only this deprecation sync — no other
  stub operations run on them.

  Status: BASELINED (2026-04-18)

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
