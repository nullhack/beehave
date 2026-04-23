Feature: Config Reading — read [tool.beehave] from pyproject.toml
Status: BASELINED (2026-04-23)

Beehave reads its configuration from the `[tool.beehave]` section in
`pyproject.toml`, applying sensible defaults for any missing keys.

Rule: Configuration is read from pyproject.toml

  @id:efed7ea2
  Example: Config keys are read from [tool.beehave]
    Given a `pyproject.toml` with `[tool.beehave]` section containing `framework = 'pytest'`
    When beehave reads configuration
    Then the framework is set to pytest

  @id:8c2aaae3
  Example: Missing config section uses defaults
    Given a `pyproject.toml` without `[tool.beehave]` section
    When beehave reads configuration
    Then all configuration values use defaults

  @id:7c4abdc7
  Example: Missing keys use defaults
    Given a `pyproject.toml` with `[tool.beehave]` but no `framework` key
    When beehave reads configuration
    Then the framework defaults to pytest
