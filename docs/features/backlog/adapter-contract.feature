Feature: Adapter-Contract — common framework adapter interface

  As a framework author or beehave contributor,
  I want a well-defined adapter contract (abstract interface / protocol)
  that specifies how a framework adapter must translate Examples into test stubs,
  so that adding support for new test frameworks is predictable and consistent.

  Adapters are registered via the `framework` key in `[tool.beehave]`
  (e.g. `framework = 'pytest'`). The `--framework <name>` CLI flag overrides the
  config value. If neither is set, `pytest` is the default.

  For v1, only built-in adapters are supported (`pytest`). The `unittest` adapter
  is parked for v2. Each adapter must provide:
  - Skip marker template
  - Deprecated marker template
  - Parametrize template (for Scenario Outlines)
  - Stub file header

  Status: BASELINED (2026-04-21)
