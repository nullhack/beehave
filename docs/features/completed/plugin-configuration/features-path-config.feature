Feature: Features path configuration
  As a developer
  I want to configure the features folder path in pyproject.toml
  So that I can use a non-default directory layout without modifying the plugin source

  @id:acf12157
  Example: Custom features path is used when configured
    Given pyproject.toml contains [tool.beehave] with features_path set to a custom directory
    When pytest is invoked
    Then the plugin reads .feature files from the configured custom directory

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

  @id:124f65e7
  Example: pytest fails when configured features path does not exist
    Given pyproject.toml contains [tool.beehave] with features_path pointing to a non-existent directory
    When pytest is invoked
    Then the pytest run exits with a non-zero status code and an error naming the missing path
