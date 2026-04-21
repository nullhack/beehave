Feature: Deprecation sync — propagate @deprecated tags to stubs

  When a Gherkin Example (or its parent Rule or Feature) carries a `@deprecated`
  tag, beehave ensures the corresponding test stub receives the framework-native
  deprecation marker (e.g., `@pytest.mark.deprecated` for pytest). When the
  `@deprecated` tag is removed from the Gherkin source, the marker is also removed
  from the stub.

  This propagation is handled as part of `sync-update` — it is one of the
  auto-generated parts of a stub that beehave is permitted to modify.

  Status: BASELINED (2026-04-21)
