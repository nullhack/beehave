Feature: Example scaffold generation

  Generates a ready-to-use `docs/features/` directory tree (or the configured features path)
  populated with bee/hive-themed Gherkin `.feature` files that exercise every plugin capability:
  auto-ID generation, stub creation, stub updates, deprecation sync, multilingual parsing, and
  the bootstrap flow. Content is partially randomised using Python stdlib only so each generated
  example feels fresh. Invoked via `pytest --beehave-sample`; fails loudly if the target directory
  already contains content unless `--beehave-sample-force` is also passed.

  Status: BASELINED (2026-04-19)

  Rules (Business):
  - The scaffold is triggered by the `--beehave-sample` pytest flag
  - The scaffold writes to the configured features path (default `docs/features/`)
  - If the target features directory already contains any `.feature` files, the command fails with a descriptive error unless `--beehave-sample-force` is passed
  - `--beehave-sample-force` overwrites existing content without prompting
  - Generated `.feature` files use bee/hive metaphors for Feature names, Rule titles, Example titles, and step text
  - Generated content showcases all plugin capabilities: tagged and untagged Examples (auto-ID), deprecated Examples, multilingual file, backlog/in-progress/completed placement, Background blocks, Scenario Outlines, and data tables
  - Randomisation uses Python stdlib only (`random`, `secrets`) — no external dependencies
  - After the scaffold runs, invoking `pytest` on the generated directory must produce stubs without errors
  - The scaffold emits a terminal summary of files written

  Constraints:
  - Must not run stub sync or any other plugin operation during the scaffold invocation — scaffold only
  - Must respect `features_path` from `[tool.beehave]` in `pyproject.toml`
  - Must exit pytest immediately after scaffold completes (no test collection)

  Rule: Scaffold invocation
    As a developer evaluating pytest-beehave
    I want to generate a complete example features directory with one command
    So that I can see all plugin capabilities working without writing any Gherkin myself

    @id:1a2b3c4d
    Example: Scaffold creates the features directory tree when it does not exist
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample
      Then the backlog, in-progress, and completed subfolders exist under the configured features path

    @id:2b3c4d5e
    Example: Scaffold writes bee-themed .feature files into the correct subfolders
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample
      Then at least one .feature file exists in each of the backlog, in-progress, and completed subfolders

    @id:3c4d5e6f
    Example: Scaffold emits a terminal summary of files written
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample
      Then the terminal output lists each .feature file that was created

    @id:4d5e6f7a
    Example: pytest exits immediately after scaffold without running tests
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample
      Then no tests are collected or executed

  Rule: Overwrite protection
    As a developer with an existing features directory
    I want the scaffold to fail loudly rather than silently overwrite my work
    So that I never lose existing feature files by accident

    @id:5e6f7a8b
    Example: Scaffold fails when the features directory already contains .feature files
      Given the configured features directory already contains at least one .feature file
      When pytest is invoked with --beehave-sample
      Then the pytest run exits with a non-zero status code and an error naming the conflicting path

    @id:6f7a8b9c
    Example: Scaffold overwrites existing content when --beehave-sample-force is passed
      Given the configured features directory already contains at least one .feature file
      When pytest is invoked with --beehave-sample --beehave-sample-force
      Then the existing .feature files are replaced with the newly generated scaffold content

  Rule: Capability showcase content
    As a developer evaluating pytest-beehave
    I want the generated Gherkin to exercise every plugin capability
    So that a single `pytest` run after scaffolding demonstrates the full feature set

    @id:7a8b9c0d
    Example: Generated content includes an untagged Example to trigger auto-ID generation
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample
      Then at least one generated .feature file contains an Example with no @id tag

    @id:8b9c0d1e
    Example: Generated content includes a @deprecated-tagged Example
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample
      Then at least one generated .feature file contains an Example tagged @deprecated

    @id:9c0d1e2f
    Example: Generated content includes a multilingual feature file
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample
      Then at least one generated .feature file begins with a # language: directive

    @id:0d1e2f3a
    Example: Generated content includes a feature with a Background block
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample
      Then at least one generated .feature file contains a Background: block

    @id:1e2f3a4b
    Example: Generated content includes a Scenario Outline with an Examples table
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample
      Then at least one generated .feature file contains a Scenario Outline with an Examples: table

  Rule: Configured path respect
    As a developer using a custom features path
    I want the scaffold to write to my configured path
    So that the generated example integrates with my project layout

    @id:2f3a4b5c
    Example: Scaffold writes to the custom path when features_path is configured
      Given pyproject.toml contains [tool.beehave] with features_path set to a custom directory
      When pytest is invoked with --beehave-sample
      Then the generated .feature files are written under the custom configured path and not under docs/features/

  Rule: Stdlib-only randomisation
    As a developer running the scaffold multiple times
    I want the generated content to vary slightly between runs
    So that the example does not feel like a static copy-paste template

    @id:3a4b5c6d
    Example: Scaffold produces different bee-themed content on successive runs
      Given no features directory exists at the configured path
      When pytest is invoked with --beehave-sample on two separate occasions
      Then the generated .feature file content differs between the two runs in at least one field

    @id:4b5c6d7e
    Example: Scaffold generation does not require any dependency beyond Python stdlib
      Given a clean Python environment with only pytest-beehave installed
      When pytest is invoked with --beehave-sample
      Then the scaffold completes successfully without importing any third-party library for randomisation
