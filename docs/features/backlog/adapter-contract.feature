Feature: Adapter-Contract — common framework adapter interface

  As a framework author or beehave contributor,
  I want a well-defined adapter contract (abstract interface / protocol)
    that specifies how a framework adapter must translate Examples into test stubs,
  so that adding support for new test frameworks is predictable and consistent.

  Adapters are selected via the `framework` key in `[tool.beehave]`
  (e.g. `framework = 'pytest'`). The `--framework <name>` CLI flag overrides the
  config value. If neither is set, `pytest` is the default.

  For v1, only built-in adapters are supported (`pytest`). The `unittest` adapter
  is parked for v2. Each adapter must provide four templates:
  - skip — marker/decorator for unimplemented tests
  - deprecated — marker/decorator for deprecated tests
  - parametrize — marker/decorator for Scenario Outline parameters
  - stub header — file-level imports and boilerplate at top of test files

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - The adapter contract is a stable protocol; v1 marks the version number.
  - Core must never import framework-specific code; all framework knowledge is
    encapsulated inside adapters.

  Constraints:
  - v1 supports only built-in adapters; external plugin entry-points are v2.

  Rule: Select adapter via configuration
    As a developer targeting a specific test framework
    I want beehave to load the correct adapter based on my config or CLI flag
    So that stubs are generated in the right format

    @id:d2e3f4a5
    Example: Default adapter is pytest
      Given a project with no `framework` key in `[tool.beehave]`
      When beehave sync runs
      Then the pytest adapter is loaded and used

    @id:e3f4a5b6
    Example: Config selects adapter
      Given a `pyproject.toml` with `[tool.beehave] framework = "pytest"`
      When beehave sync runs
      Then the pytest adapter is loaded and used

    @id:f4a5b6c7
    Example: CLI flag overrides config
      Given a `pyproject.toml` with `[tool.beehave] framework = "pytest"`
      When I run `beehave sync --framework unittest`
      Then the unittest adapter is loaded for this invocation only

  Rule: Adapter supplies all marker templates
    As a framework author implementing a new adapter
    I want my adapter to provide every template the core needs
    So that the core stays framework-agnostic

    @id:a5b6c7d8
    Example: Missing template raises clear error
      Given a skeleton adapter that omits the `parametrize` template
      When beehave attempts a sync involving a Scenario Outline
      Then a hard error is raised naming the missing template and the adapter

  Rule: Adapter API is versioned
    As a beehave maintainer
    I want the adapter protocol to have a declared version
    So that I can evolve it without silently breaking third-party adapters

    @id:b6c7d8e9
    Example: Future adapter with v2 contract
      Given a hypothetical v2 adapter installed
      When beehave v1 attempts to load it
      Then a version mismatch error is raised indicating beehave v1 is required
