Feature: Example hatch generation

  Generates a ready-to-use `docs/features/` directory tree (or the configured features path)
  populated with bee/hive-themed Gherkin `.feature` files that exercise every plugin capability:
  auto-ID generation, stub creation, stub updates, deprecation sync, multilingual parsing, and
  the bootstrap flow. Content is partially randomised using Python stdlib only so each generated
  example feels fresh. Invoked via `pytest --beehave-hatch`; fails loudly if the target directory
  already contains content unless `--beehave-hatch-force` is also passed.

  Status: BASELINED (2026-04-19)

  Rules (Business):
  - The hatch is triggered by the `--beehave-hatch` pytest flag
  - The hatch writes to the configured features path (default `docs/features/`)
  - If the target features directory already contains any `.feature` files, the command fails with a descriptive error unless `--beehave-hatch-force` is passed
  - `--beehave-hatch-force` overwrites existing content without prompting
  - Generated `.feature` files use bee/hive metaphors for Feature names, Rule titles, Example titles, and step text
  - Generated content showcases all plugin capabilities: tagged and untagged Examples (auto-ID), deprecated Examples, multilingual file, backlog/in-progress/completed placement, Background blocks, Scenario Outlines, and data tables
  - Randomisation uses Python stdlib only (`random`, `secrets`) — no external dependencies
  - After the hatch runs, invoking `pytest` on the generated directory must produce stubs without errors
  - The hatch emits a terminal summary of files written

  Constraints:
  - Must not run stub sync or any other plugin operation during the hatch invocation — hatch only
  - Must respect `features_path` from `[tool.beehave]` in `pyproject.toml`
  - Must exit pytest immediately after hatch completes (no test collection)

  Rule: Hatch invocation
    As a developer evaluating pytest-beehave
    I want to generate a complete example features directory with one command
    So that I can see all plugin capabilities working without writing any Gherkin myself

    @id:1a2b3c4d
    Example: Hatch creates the features directory tree when it does not exist
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then the backlog, in-progress, and completed subfolders exist under the configured features path

    @id:2b3c4d5e
    Example: Hatch writes bee-themed .feature files into the correct subfolders
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then at least one .feature file exists in each of the backlog, in-progress, and completed subfolders

    @id:3c4d5e6f
    Example: Hatch emits a terminal summary of files written
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then the terminal output lists each .feature file that was created

    @id:4d5e6f7a
    Example: pytest exits immediately after hatch without running tests
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then no tests are collected or executed

  Rule: Overwrite protection
    As a developer with an existing features directory
    I want the hatch to fail loudly rather than silently overwrite my work
    So that I never lose existing feature files by accident

    @id:5e6f7a8b
    Example: Hatch fails when the features directory already contains .feature files
      Given the configured features directory already contains at least one .feature file
      When pytest is invoked with --beehave-hatch
      Then the pytest run exits with a non-zero status code and an error naming the conflicting path

    @id:6f7a8b9c
    Example: Hatch overwrites existing content when --beehave-hatch-force is passed
      Given the configured features directory already contains at least one .feature file
      When pytest is invoked with --beehave-hatch --beehave-hatch-force
      Then the existing .feature files are replaced with the newly generated hatch content

  Rule: Capability showcase content
    As a developer evaluating pytest-beehave
    I want the generated Gherkin to exercise every plugin capability
    So that a single `pytest` run after hatching demonstrates the full feature set

    @id:7a8b9c0d
    Example: Generated content includes an untagged Example to trigger auto-ID generation
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then at least one generated .feature file contains an Example with no @id tag

    @id:8b9c0d1e
    Example: Generated content includes a @deprecated-tagged Example
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then at least one generated .feature file contains an Example tagged @deprecated

    @id:9c0d1e2f
    Example: Generated content includes a multilingual feature file
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then at least one generated .feature file begins with a # language: directive

    @id:0d1e2f3a
    Example: Generated content includes a feature with a Background block
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then at least one generated .feature file contains a Background: block

    @id:1e2f3a4b
    Example: Generated content includes a Scenario Outline with an Examples table
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then at least one generated .feature file contains a Scenario Outline with an Examples: table

    @id:a1f2e3d4
    Example: Generated content includes a step with an attached data table
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then at least one generated .feature file contains a step followed by a data table

    @id:b2e3d4c5
    Example: Generated content includes a feature placed in the completed subfolder
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch
      Then at least one generated .feature file is placed in the completed subfolder

  Rule: Configured path respect
    As a developer using a custom features path
    I want the hatch to write to my configured path
    So that the generated example integrates with my project layout

    @id:c3d4e5f6
    Example: Hatch writes to the custom path when features_path is configured
      Given pyproject.toml contains [tool.beehave] with features_path set to a custom directory
      When pytest is invoked with --beehave-hatch
      Then the generated .feature files are written under the custom configured path and not under docs/features/

  Rule: Stdlib-only randomisation
    As a developer running the hatch multiple times
    I want the generated content to vary slightly between runs
    So that the example does not feel like a static copy-paste template

    @id:d4e5f6a7
    Example: Hatch produces a different Feature name on successive runs
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-hatch on two separate occasions with the directory removed between runs
      Then the Feature name in the generated .feature file differs between the two runs

    @id:e5f6a7b8
    Example: Hatch completes without requiring any additional package installation
      Given a clean environment with only pytest-beehave installed and no other packages
      When pytest is invoked with --beehave-hatch
      Then the hatch completes successfully and no import error or missing-module error is raised
