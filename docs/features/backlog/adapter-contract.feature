Feature: Adapter Contract — common framework adapter interface
Status: BASELINED (2026-04-23)

Beehave uses a pluggable adapter system where each test framework supplies
marker templates and conventions. Adapters are registered via config or CLI
flag. v1 ships with the pytest adapter only; unittest is parked for v2.

Rule: Adapter registration

  @id:1635448b
  Example: Adapter via config
    Given `framework = 'pytest'` is set in `[tool.beehave]`
    When beehave sync runs
    Then the pytest adapter is used

  @id:db46e7bb
  Example: CLI flag overrides config
    Given `framework = 'pytest'` is set in `[tool.beehave]`
    When the user runs "beehave sync --framework unittest"
    Then the unittest adapter is used

  @id:b2c4e9ca
  Example: Default is pytest
    Given no framework is specified in config or CLI
    When beehave sync runs
    Then the pytest adapter is used

Rule: Adapter provides marker templates

  @id:39abfbe8
  Example: Each adapter supplies skip marker, deprecated marker, parametrize template, and stub header
    Given the pytest adapter is active
    Then it provides:
      | Template | Value |
      | Skip marker | `@pytest.mark.skip(reason="not yet implemented")` |
      | Deprecated marker | `@pytest.mark.deprecated` |
      | Parametrize | `@pytest.mark.parametrize(...)` |
      | Stub header | pytest imports and conventions |
