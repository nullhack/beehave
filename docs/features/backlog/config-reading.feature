Feature: Config reading — read and apply tool configuration

  Beehave reads its runtime configuration from `pyproject.toml` under the
  `[tool.beehave]` section. This single source of truth keeps configuration
  discoverable, version-controlled, and discoverable by other tooling.

  The parser applies sensible defaults for every key so that a project works
  without any explicit configuration. Unknown or malformed keys produce a hard
  error with a clear message — beehave never silently ignore bad config.

  CLI flags always override config-file values.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - One config file per project: `pyproject.toml` only.
  - Defaults must be sufficient for a green-field project to work.

  Constraints:
  - No other config file formats are supported in v1.

  Rule: Load configuration from pyproject.toml
    As a developer configuring beehave
    I want values in `[tool.beehave]` to be picked up automatically
    So that I don't have to repeat them on every CLI invocation

    @id:e1f2a3b4
    Example: Reads features_path from config
      Given a `pyproject.toml` with `[tool.beehave] features_path = "specs"`
      When beehave scans for `.feature` files
      Then it looks in `specs/` instead of the default `docs/features/`

    @id:f2a3b4c5
    Example: Reads framework adapter from config
      Given a `pyproject.toml` with `[tool.beehave] framework = "pytest"`
      When beehave generates stubs
      Then it uses the pytest adapter

  Rule: Apply hard-coded defaults when key is absent
    As a developer on a green-field project
    I want beehave to work even when I have not set any config
    So that I can start experimenting immediately

    @id:a3b4c5d6
    Example: All defaults are documentable
      Given a project with no `[tool.beehave]` section (or an empty one)
      When beehave loads config
      Then the effective config equals the documented default values

  Rule: Hard error on invalid config
    As a developer who made a typo
    I want beehave to tell me immediately that my config is wrong
    So that I don't waste time debugging mysterious silent misbehaviour

    @id:b4c5d6e7
    Example: Unknown key produces hard error
      Given a `pyproject.toml` with `[tool.beehave] unknwon_key = true`
      When beehave loads config
      Then the command exits with an error and the message names the unknown key

    @id:c5d6e7f8
    Example: Wrong type produces hard error
      Given a `pyproject.toml` with `[tool.beehave] features_path = 123`
      When beehave loads config
      Then the command exits with an error and the message names the bad key

  Rule: CLI flags override config values
    As a developer testing a different adapter temporarily
    I want command-line arguments to take precedence over the config file
    So that I can run one-off experiments without editing files

    @id:d6e7f8a9
    Example: --framework flag overrides config
      Given a `pyproject.toml` with `[tool.beehave] framework = "pytest"`
      When I run `beehave sync --framework unittest`
      Then beehave uses the unittest adapter for this invocation only
