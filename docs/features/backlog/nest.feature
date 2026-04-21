Feature: Nest — bootstrap canonical directory structure

  `beehave nest` initialises the canonical beehave directory structure in a
  project. On a green-field project it creates five directories — the root
  `docs/features/` folder, its three stage subfolders (`backlog/`,
  `in-progress/`, `completed/`), and `tests/features/` — each seeded with a
  `.gitkeep` so they are tracked by git. It also injects a `[tool.beehave]`
  configuration snippet into `pyproject.toml` if the section is absent.

  The command is additive and idempotent: running it a second time only creates
  whatever is still missing and emits a configurable warning (or error) when the
  project is already fully nested. A project is considered "already nested" when
  `docs/features/` already contains at least one `.feature` file.

  `beehave nest` never generates `.feature` content — that is `hatch`'s job.
  It never refuses or prompts because of unrelated files already present.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - Managed paths are only those inside the configured features root and
    `tests/features/`; no other paths are touched.
  - `--check` never modifies anything; it only verifies and reports via exit code.

  Constraints:
  - `pyproject.toml` injection is additive only; existing `[tool.beehave]` content
    is never overwritten or merged.

  Rule: Create canonical directories
    As a developer starting a new project
    I want `beehave nest` to create the standard docs and tests directories
    So that I have a predictable place for `.feature` files and test stubs

    @id:a1b2c3d4
    Example: Green-field project gets all five directories
      Given a project with no `docs/features/` directory
      When I run `beehave nest`
      Then the directories `docs/features/`, `docs/features/backlog/`,
        `docs/features/in-progress/`, `docs/features/completed/`, and
        `tests/features/` all exist

    @id:b2c3d4e5
    Example: Additive on partially existing structure
      Given a project where `docs/features/` already exists but
        `tests/features/` does not
      When I run `beehave nest`
      Then `tests/features/` is created and the existing `docs/features/`
        is left unchanged

    @id:c3d4e5f6
    Example: Custom features root via CLI flag
      Given a project with no feature directories
      When I run `beehave nest --features-dir specs/features`
      Then `specs/features/`, `specs/features/backlog/`,
        `specs/features/in-progress/`, `specs/features/completed/`, and
        `tests/features/` all exist

    @id:d4e5f6a7
    Example: Warning when project is already nested
      Given a project where `docs/features/` already contains a `.feature` file
      When I run `beehave nest`
      Then the command exits 0 and emits a warning that the project is
        already nested

  Rule: Seed directories with .gitkeep
    As a developer using git
    I want empty directories to contain a `.gitkeep` file
    So that git tracks them even before any `.feature` files are added

    @id:e5f6a7b8
    Example: Every empty managed directory gets .gitkeep
      Given a green-field project
      When I run `beehave nest`
      Then every created directory contains a `.gitkeep` file

  Rule: Inject tool configuration
    As a developer configuring beehave
    I want `pyproject.toml` to contain a default `[tool.beehave]` section
    So that I can see which keys are available without reading docs

    @id:f6a7b8c9
    Example: Injects section when pyproject.toml exists but lacks tool.beehave
      Given a project with a `pyproject.toml` that has no `[tool.beehave]` section
      When I run `beehave nest`
      Then `pyproject.toml` now contains a `[tool.beehave]` section with
        key placeholders and their default values

    @id:a7b8c9d0
    Example: Does not touch existing tool.beehave content
      Given a project with a `pyproject.toml` that already has `[tool.beehave]`
      When I run `beehave nest`
      Then the existing `[tool.beehave]` content is unchanged

  Rule: Verify structure without modifying
    As a CI pipeline maintainer
    I want to check that the project structure is complete before running tests
    So that missing directories are caught early

    @id:b8c9d0e1
    Example: Passes when all directories exist
      Given a fully nested project
      When I run `beehave nest --check`
      Then the command exits 0 and produces no output

    @id:c9d0e1f2
    Example: Fails when a managed directory is missing
      Given a project where `docs/features/in-progress/` is missing
      When I run `beehave nest --check`
      Then the command exits non-zero and the output names the missing path

  Rule: Overwrite existing structure
    As a developer resetting project conventions
    I want to forcefully recreate the managed directories
    So that I can recover from accidental manual changes to the layout

    @id:d0e1f2a3
    Example: Overwrite removes and recreates managed directories
      Given a fully nested project with extra files inside `tests/features/`
      When I run `beehave nest --overwrite`
      Then the managed directories are recreated and any extra files inside
        them are removed
