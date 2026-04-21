Feature: Features path configuration

  Status: BASELINED (2026-04-18)

  Rules (Business):
  - Configuration lives in `[tool.beehave]` section of `pyproject.toml`
  - The only configurable option is `features_path` (path to the features directory)
  - Default value: `docs/features/` relative to the project root (where `pyproject.toml` lives)
  - The path is resolved relative to the directory containing `pyproject.toml`
  - If `pyproject.toml` does not exist or has no `[tool.beehave]` section, the default is used silently
  - The plugin is always-on; there is no enable/disable switch

  Constraints:
  - Must not fail if `pyproject.toml` is absent — fall back to default
  - Must not fail if `[tool.beehave]` section is absent — fall back to default
  - Must produce a clear error if `features_path` is configured but the directory does not exist

  Rule: Custom features path
    As a developer
    I want to configure the features folder path in pyproject.toml
    So that I can use a non-default directory layout without modifying the plugin source

    @id:acf12157
    Example: Custom features path is used when configured
      Given pyproject.toml contains [tool.beehave] with features_path set to a custom directory
      When pytest is invoked
      Then the plugin reads .feature files from the configured custom directory

    @id:124f65e7
    Example: pytest fails when configured features path does not exist
      Given pyproject.toml contains [tool.beehave] with features_path pointing to a non-existent directory
      When pytest is invoked
      Then the pytest run exits with a non-zero status code and an error naming the missing path

  Rule: Default features path
    As a developer
    I want the features folder to default to docs/features/
    So that it works out of the box without configuration

    @id:ce8a95e7
    Example: Default features path is used when no configuration is present
      Given pyproject.toml contains no [tool.beehave] section
      When pytest is invoked
      Then the plugin reads .feature files from docs/features/ relative to the project root

    @id:aaeda817
    Example: Default features path is used when pyproject.toml is absent
      Given no pyproject.toml exists in the project root
      When pytest is invoked
      Then the plugin reads .feature files from docs/features/ relative to the project root
