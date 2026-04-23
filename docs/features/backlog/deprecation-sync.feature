Feature: Deprecation Sync — propagate @deprecated tags to stubs
Status: BASELINED (2026-04-23)

Beehave propagates `@deprecated` tags from `.feature` files to the
corresponding test stubs. The cascade is absolute: a `@deprecated` tag on a
Feature or Rule applies to all Examples beneath it with NO override in v1.

Rule: @deprecated cascades from Feature and Rule to all child Examples

  @id:c1f44d6c
  Example: @deprecated on Feature cascades to all Examples
    Given a Feature tagged `@deprecated` with three Examples
    When beehave sync runs
    Then all three corresponding stubs receive the deprecated marker

  @id:3f9939c1
  Example: @deprecated on Rule cascades to all Examples under that Rule
    Given a Rule tagged `@deprecated` with two Examples
    When beehave sync runs
    Then both corresponding stubs receive the deprecated marker

  @id:7e966f90
  Example: No override mechanism in v1
    Given a Feature tagged `@deprecated`
    And an Example under it that should not be deprecated
    When beehave sync runs
    Then the Example's stub still receives the deprecated marker

Rule: @deprecated is propagated as adapter-specific marker

  @id:d3f502c3
  Example: Pytest adapter uses @pytest.mark.deprecated
    Given the pytest adapter is active
    And an Example is affected by `@deprecated`
    When beehave sync runs
    Then the stub is decorated with `@pytest.mark.deprecated`
