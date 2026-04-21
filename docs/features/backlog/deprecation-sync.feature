Feature: Deprecation sync — propagate @deprecated tags to stubs

  When a Gherkin Example (or its parent Rule or Feature) carries a `@deprecated`
  tag, beehave ensures the corresponding test stub receives the framework-native
  deprecation marker (e.g., `@pytest.mark.deprecated`). When the tag is removed,
  the marker is also removed.

  Status: DRAFT
