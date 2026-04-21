Feature: pytest lifecycle integration

  Status: BASELINED (2026-04-18)

  Rules (Business):
  - The plugin registers itself automatically via `entry_points` in `pyproject.toml` — no manual `conftest.py` required
  - The stub sync runs before pytest collection so that any newly generated stubs are discovered and collected in the same `pytest` invocation
  - The plugin is always-on; there is no configuration option to disable it

  Constraints:
  - Must not break pytest collection if the features directory does not exist or is empty
  - Must be compatible with pytest ≥ 6.0
  - Entry point key: `pytest11`

  Rule: Stub sync runs before collection
    As a developer
    I want the stub sync to run automatically when I invoke pytest
    So that my test stubs are always in sync with my acceptance criteria without a manual step

    @id:bde8de30
    Example: Stub sync runs before test collection
      Given a project with a backlog feature containing a new Example with an @id tag
      When pytest is invoked
      Then the test stub for that Example exists before any tests are collected

    @id:d5824c75
    Example: Plugin reports sync actions to the terminal
      Given a project with a backlog feature containing a new Example
      When pytest is invoked
      Then the terminal output includes a summary of the stub sync actions taken

  Rule: Graceful handling
    As a developer
    I want the plugin to handle missing features directories gracefully
    So that pytest completes without errors even when no features are configured

    @id:d0f2866d
    Example: Plugin skips sync and continues when the default features directory is absent
      Given no pyproject.toml [tool.beehave] section is present and the default docs/features/ directory does not exist
      When pytest is invoked
      Then pytest completes collection without errors

    @deprecated @id:e3a13b58
    @id:39654ea7
    Example: Plugin does not crash when configured features directory is absent
      Given a project where the configured features directory does not exist
      When pytest is invoked
      Then pytest completes collection without errors
