Feature: Nest — bootstrap canonical directory structure
Status: BASELINED (2026-04-23)

`beehave nest` creates the standard directory structure for a beehave-managed
project and injects the `[tool.beehave]` configuration snippet into
`pyproject.toml`. It is run once per repository and is idempotent.

Rule: Nest creates required directories on a green-field project

  @id:bc2403aa
  Example: Green-field project gets all directories
    Given a project without any beehave directories
    When the user runs "beehave nest"
    Then the following directories are created with `.gitkeep` files:
      | Path |
      | docs/features/ |
      | docs/features/backlog/ |
      | docs/features/in-progress/ |
      | docs/features/completed/ |
      | tests/features/ |

  @id:4ec46e2c
  Example: Green-field project gets pyproject.toml injection
    Given a project without `[tool.beehave]` in `pyproject.toml`
    When the user runs "beehave nest"
    Then a `[tool.beehave]` snippet is injected into `pyproject.toml`

Rule: Nest is idempotent and additive

  @id:5bba6867
  Example: Running nest twice does not destroy existing content
    Given a project that is already fully nested
    When the user runs "beehave nest"
    Then no existing files or directories are removed or overwritten
    And a warning is issued that the project is already nested

  @id:9e6d9a7b
  Example: Partial structure is completed
    Given a project that has `docs/features/` but not `docs/features/backlog/`
    When the user runs "beehave nest"
    Then only the missing directories are created
    And existing directories and their contents are left unchanged

  @id:15d18e4b
  Example: Unrelated files are not disturbed
    Given a project with unrelated files in `docs/features/`
    When the user runs "beehave nest"
    Then the missing subdirectories are created
    And the unrelated files remain untouched

Rule: Nest supports non-default layout

  @id:ba3004bd
  Example: Custom features directory via flag
    Given a project without beehave directories
    When the user runs "beehave nest --features-dir spec/features/"
    Then the directory structure is created under `spec/features/`

Rule: Nest supports --check mode for CI

  @id:67075383
  Example: Check mode verifies structure without modifying
    Given a project that is fully nested
    When the user runs "beehave nest --check"
    Then the command exits with code 0
    And no files are modified

  @id:c055b222
  Example: Check mode fails when structure is incomplete
    Given a project missing `tests/features/`
    When the user runs "beehave nest --check"
    Then the command exits with code 1

Rule: Nest supports --overwrite flag

  @id:a5ee2460
  Example: Overwrite recreates structure from scratch
    Given a project that is already nested
    When the user runs "beehave nest --overwrite"
    Then all managed directories are removed and recreated
