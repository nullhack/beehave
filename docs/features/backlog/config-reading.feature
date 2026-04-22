Feature: config-reading — read [tool.beehave] from pyproject.toml

  Reads beehave configuration from the [tool.beehave] table in pyproject.toml located in the
  working directory. Provides defaults for all config keys so beehave works out of the box
  without any configuration. CLI flags override config file values for the current invocation only.

  Status: ELICITING

  Rules (Business):
  - Missing config keys fall back to documented defaults
  - CLI flags override config file values for the current invocation

  Constraints:
  - Config file location: pyproject.toml in the current working directory
  - Supported keys (v1): framework, features_dir, template_path
