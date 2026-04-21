Feature: Deprecation sync — propagate @deprecated tags to stubs

  When a Gherkin Example (or its parent Rule or Feature) carries a `@deprecated`
  tag, beehave ensures the corresponding test stub receives the framework-native
  deprecation marker (e.g., `@pytest.mark.deprecated` for pytest). When the
  `@deprecated` tag is removed from the Gherkin source, the marker is also removed
  from the stub.

  This propagation is handled as part of `sync-update` — it is one of the
  auto-generated parts of a stub that beehave is permitted to modify.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - A `@deprecated` tag on a Feature or Rule applies to all Examples beneath it.
  - `@deprecated` on an Example overrides any inherited deprecated state.

  Constraints:
  - Frameworks without a native deprecation mechanism receive a no-op or comment
    marker instead of a hard error.

  Rule: Propagate @deprecated from Example to stub
    As a developer deprecating a scenario
    I want the corresponding test stub to be marked deprecated automatically
    So that my test runner skips or warns about it appropriately

    @id:f2a3b4c5
    Example: Example gains @deprecated tag
      Given a `.feature` Example newly tagged with `@deprecated`
        and a matching test stub without a deprecation marker
      When beehave sync runs
      Then the stub receives the adapter's deprecated marker

    @id:a3b4c5d6
    Example: Example loses @deprecated tag
      Given a `.feature` Example where the `@deprecated` tag was removed
        and a matching test stub with a deprecation marker
      When beehave sync runs
      Then the deprecation marker is removed from the stub

  Rule: Inherit @deprecated from parent Rule or Feature
    As a developer marking an entire Rule as deprecated
    I want all Examples under that Rule to be deprecated without tagging each one
    So that deprecation is DRY

    @id:b4c5d6e7
    Example: Rule with @deprecated deprecates all child Examples
      Given a `.feature` Rule tagged with `@deprecated` containing two Examples
      When beehave sync runs
      Then both test stubs receive the adapter's deprecated marker even though
        the individual Examples have no `@deprecated` tag

    @id:c5d6e7f8
    Example: Feature with @deprecated deprecates all Rules and Examples
      Given a `.feature` Feature tagged with `@deprecated` containing Rules
        and Examples without individual `@deprecated` tags
      When beehave sync runs
      Then all test stubs in that feature receive the adapter's deprecated marker

