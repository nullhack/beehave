Feature: deprecation-sync — propagate @deprecated tags to test stubs

  When a .feature file carries a @deprecated tag at Feature, Rule, or Example level, beehave
  sync adds the adapter's deprecated marker to all affected test stub functions. The cascade is
  absolute in v1: a @deprecated on a Feature or Rule propagates to every child Example with no
  per-Example override mechanism.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - @deprecated on a Feature applies to all child Examples of that Feature
  - @deprecated on a Rule applies to all child Examples of that Rule
  - @deprecated on an Example applies to that Example only
  - There is no per-Example override of a parent @deprecated tag in v1

  Constraints:
  - Cascade direction is always parent → child; never child → parent

  Rule: Example-level deprecation
    As a developer
    I want beehave to mark a stub as deprecated when its Example is tagged @deprecated
    So that pytest can report it accordingly

    @id:2afe7190
    Example: @deprecated on Example adds deprecated marker to its stub
      Given an Example tagged @deprecated
      When beehave sync runs
      Then the corresponding stub function has the adapter's deprecated marker

    @id:428a5348
    Example: Removing @deprecated from Example removes the marker from its stub
      Given a stub with the deprecated marker whose Example no longer has @deprecated
      When beehave sync runs
      Then the deprecated marker is removed from the stub function

  Rule: Rule-level deprecation cascade
    As a developer
    I want @deprecated on a Rule to propagate to all its child Examples
    So that deprecating a user story marks all its tests as deprecated in one step

    @id:55faf7b9
    Example: @deprecated on Rule adds deprecated marker to all child stubs
      Given a Rule tagged @deprecated containing three Examples
      When beehave sync runs
      Then all three corresponding stub functions have the adapter's deprecated marker

    @id:a7ad94e7
    Example: Only the Rule's child stubs are affected; sibling Rule stubs are unchanged
      Given two Rules where only the first is tagged @deprecated
      When beehave sync runs
      Then only stubs under the first Rule have the deprecated marker; the second Rule's stubs are unchanged

  Rule: Feature-level deprecation cascade
    As a developer
    I want @deprecated on a Feature to propagate to all Examples in that Feature
    So that deprecating an entire feature marks every test in one step

    @id:e94de52f
    Example: @deprecated on Feature adds deprecated marker to all stubs in the feature
      Given a Feature tagged @deprecated with two Rules and four Examples total
      When beehave sync runs
      Then all four stub functions have the adapter's deprecated marker

  Rule: No per-Example override in v1
    As a developer
    I want the cascade to be absolute so the behaviour is predictable
    So that I do not need to track which Examples have been individually overridden

    @id:62b7aac9
    Example: An Example cannot override a parent @deprecated tag in v1
      Given a Rule tagged @deprecated and one of its Examples also tagged @deprecated
      When beehave sync runs
      Then the stub for that Example has the deprecated marker (same as all other children; no special treatment)
