Feature: pytest lifecycle integration
  As a developer
  I want the stub sync to run automatically when I invoke pytest
  So that my test stubs are always in sync with my acceptance criteria without a manual step

  @id:bde8de30
  Example: Stub sync runs before test collection
    Given a project with a backlog feature containing a new Example with an @id tag
    When pytest is invoked
    Then the test stub for that Example exists before any tests are collected

  @deprecated @id:e3a13b58
  Example: Plugin does not crash when features directory is absent
    Given a project where the configured features directory does not exist
    When pytest is invoked
    Then pytest completes collection without errors

  @id:d0f2866d
  Example: Plugin skips sync and continues when the default features directory is absent
    Given no pyproject.toml [tool.beehave] section is present and the default docs/features/ directory does not exist
    When pytest is invoked
    Then pytest completes collection without errors

  @id:d5824c75
  Example: Plugin reports sync actions to the terminal
    Given a project with a backlog feature containing a new Example
    When pytest is invoked
    Then the terminal output includes a summary of the stub sync actions taken
