Feature: nest — bootstrap canonical directory structure

  Bootstraps the required directory structure and configuration for a new beehave project.
  Running `beehave nest` creates docs/features/{backlog,in-progress,completed}/, tests/features/,
  and .gitkeep files in each empty directory. It also injects a [tool.beehave] snippet into
  pyproject.toml if not already present. The command is additive and idempotent.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - Nest never removes or overwrites existing content
  - A project is considered already nested if docs/features/ contains any .feature file
  - nest --check verifies structure without modifying anything and exits non-zero if incomplete
  - nest --overwrite recreates managed directories from scratch

  Constraints:
  - Accepts --features-dir to override the default docs/features/ path
  - Safe to run in an existing Python project with unrelated files present

  Rule: Directory bootstrapping
    As a developer
    I want beehave nest to create the required directory structure
    So that I can start using beehave immediately in a new project

    @id:d9b7b520
    Example: Creates all required directories in a clean project
      Given a project directory with no beehave structure
      When beehave nest is run
      Then docs/features/backlog/, docs/features/in-progress/, docs/features/completed/, and tests/features/ all exist

    @id:2b76d9eb
    Example: Places .gitkeep in each new empty directory
      Given a project directory with no beehave structure
      When beehave nest is run
      Then each created empty directory contains a .gitkeep file

    @id:6f29a8f2
    Example: Injects [tool.beehave] into pyproject.toml when absent
      Given a pyproject.toml with no [tool.beehave] section
      When beehave nest is run
      Then pyproject.toml contains a [tool.beehave] section with default key-value pairs

  Rule: Idempotency and safety
    As a developer
    I want beehave nest to be safe to re-run on an existing project
    So that I can run it in CI or after a pull without fear of data loss

    @id:8236b93e
    Example: Existing directories are not modified
      Given a project with docs/features/backlog/ already containing a .feature file
      When beehave nest is run
      Then the existing .feature file is unchanged

    @id:580ba508
    Example: Existing [tool.beehave] section is not overwritten
      Given a pyproject.toml with a [tool.beehave] section containing custom values
      When beehave nest is run
      Then the existing [tool.beehave] values are unchanged

    @id:86e134b6
    Example: Running nest twice produces the same result as running it once
      Given a clean project
      When beehave nest is run twice in succession
      Then the resulting structure is identical to running it once

  Rule: Check mode
    As a developer
    I want nest --check to verify structure without writing anything
    So that CI can enforce that the project structure is correct

    @id:4a676e83
    Example: Exits 0 when structure is complete
      Given a project with all required beehave directories present
      When beehave nest --check is run
      Then the exit code is 0 and no files are written

    @id:c5bc7117
    Example: Exits non-zero when structure is incomplete
      Given a project missing docs/features/completed/
      When beehave nest --check is run
      Then the exit code is non-zero and no files are written

  Rule: Overwrite mode
    As a developer
    I want nest --overwrite to recreate managed directories from scratch
    So that I can reset a corrupted or misconfigured structure

    @id:58c68617
    Example: Recreates managed directories when --overwrite is set
      Given a project where docs/features/backlog/ has been deleted
      When beehave nest --overwrite is run
      Then all managed directories are recreated with .gitkeep files
