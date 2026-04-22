Feature: config-reading — read [tool.beehave] from pyproject.toml

  Reads beehave configuration from the [tool.beehave] table in pyproject.toml located in the
  working directory. Provides defaults for all config keys so beehave works out of the box
  without any configuration. CLI flags override config file values for the current invocation only.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - Missing config keys fall back to documented defaults
  - CLI flags override config file values for the current invocation

  Constraints:
  - Config file location: pyproject.toml in the current working directory
  - Supported keys (v1): framework, features_dir, template_path, on_delete, on_orphan, log_level

  Rule: Default configuration
    As a developer
    I want beehave to work without any configuration file
    So that I can use it immediately after installation

    @id:3103f573
    Example: All defaults when no pyproject.toml exists
      Given no pyproject.toml in the working directory
      When beehave loads configuration
      Then framework is "pytest", features_dir is "docs/features", template_path is None, on_delete is "warn", on_orphan is "warn", log_level is "WARNING"

    @id:d20cc79f
    Example: All defaults when [tool.beehave] section is absent
      Given a pyproject.toml with no [tool.beehave] section
      When beehave loads configuration
      Then all keys use their documented default values

    @id:9e21706a
    Example: Partial config uses defaults for missing keys
      Given a pyproject.toml with [tool.beehave] containing only framework = "pytest"
      When beehave loads configuration
      Then framework is "pytest" and all other keys use their defaults

  Rule: Config file reading
    As a developer
    I want beehave to read my [tool.beehave] settings from pyproject.toml
    So that I can configure it once per project

    @id:1ff9caa3
    Example: All supported keys are read
      Given a pyproject.toml with [tool.beehave] setting all six supported keys
      When beehave loads configuration
      Then each key reflects the value from the config file

    @id:26bafb7e
    Example: Malformed pyproject.toml raises an error
      Given a pyproject.toml that is not valid TOML
      When beehave loads configuration
      Then beehave exits with an error describing the parse failure

    @id:a1682833
    Example: Unknown keys in [tool.beehave] are ignored
      Given a pyproject.toml with [tool.beehave] containing an unrecognised key
      When beehave loads configuration
      Then beehave loads successfully and the unknown key is silently ignored

  Rule: CLI flag override
    As a developer
    I want CLI flags to override config file values for the current invocation
    So that I can run one-off commands without editing pyproject.toml

    @id:8d5722f3
    Example: --framework flag overrides config file value
      Given a pyproject.toml with framework = "pytest"
      When beehave is invoked with --framework pytest
      Then framework for this invocation is "pytest" regardless of config

    @id:96807b94
    Example: --features-dir flag overrides features_dir
      Given a pyproject.toml with features_dir = "docs/features"
      When beehave is invoked with --features-dir custom/path
      Then features_dir for this invocation is "custom/path"

    @id:13869c93
    Example: CLI override does not persist to pyproject.toml
      Given a pyproject.toml with features_dir = "docs/features"
      When beehave is invoked with --features-dir custom/path and completes
      Then pyproject.toml still contains features_dir = "docs/features"
