Feature: pytest lifecycle integration

  Discovery:

  Status: BASELINED

  Entities:
  | Type | Name | Candidate Class/Method | In Scope |
  |------|------|----------------------|----------|
  | Noun | pytest plugin | `BeehavePlugin` | Yes |
  | Noun | pytest session | pytest lifecycle | Yes |
  | Noun | pytest config | `pytest_configure` hook | Yes |
  | Noun | stub sync | full sync operation | Yes |
  | Verb | register plugin | `pytest_configure` entry point | Yes |
  | Verb | run before collection | `pytest_sessionstart` or `pytest_collection_start` | Yes |
  | Verb | trigger stub sync | invoke sync logic before collection | Yes |

  Rules (Business):
  - The plugin registers itself automatically via `entry_points` in `pyproject.toml` — no manual `conftest.py` required
  - The stub sync runs before pytest collection so that any newly generated stubs are discovered and collected in the same `pytest` invocation
  - The plugin is always-on; there is no configuration option to disable it

  Constraints:
  - Must not break pytest collection if the features directory does not exist or is empty
  - Must be compatible with pytest ≥ 6.0
  - Entry point key: `pytest11`

  Questions:
  | ID | Question | Answer | Status |
  |----|----------|--------|--------|
  | Q1 | Which pytest hook runs before collection? | `pytest_configure` runs at startup before collection; `pytest_sessionstart` runs after collection starts — use `pytest_configure` or a custom `pytest_collection_start` hook | ANSWERED |
  | Q2 | Should the plugin emit any output to the pytest terminal during sync? | Yes — brief summary of actions taken (same style as current script) | ANSWERED |

  All questions answered. Discovery frozen.

  Architecture:

  ### Module Structure
  - `pytest_beehave/plugin.py` — `pytest_configure(config: pytest.Config) -> None` hook; reads `BeehaveConfig` via `read_config`, calls `bootstrap_features_directory`, calls `run_sync`, reports via `reporter` module. `_RealFileSystem` adapter (implements `FileSystemProtocol`). `_PytestTerminalWriter` adapter (implements `TerminalWriterProtocol`).
  - `pytest_beehave/sync_engine.py` — `run_sync(features_root, tests_root, filesystem) -> SyncResult`; orchestrates the full pipeline: discover → ID write-back → stub create/update → orphan/non-conforming → deprecation sync. `SyncResult` frozen dataclass. `discover_feature_locations(features_root) -> list[FeatureLocation]`.
  - `pytest_beehave/reporter.py` — `report_bootstrap`, `report_id_write_back`, `report_sync_actions`; all accept a `TerminalWriterProtocol`. `TerminalWriterProtocol` Protocol class.

  ### Key Decisions
  ADR-001: Use pytest_configure hook (not pytest_sessionstart) for pre-collection sync
  Decision: Run stub sync inside `pytest_configure` so stubs exist before collection begins.
  Reason: `pytest_configure` is called before collection; `pytest_sessionstart` is called after — using the latter would miss newly generated stubs in the same run.
  Alternatives considered: `pytest_collection_start` — not a standard hook; `pytest_sessionstart` — runs too late.

  ADR-002: Inject filesystem and terminal writer as Protocol adapters
  Decision: `plugin.py` instantiates `_RealFileSystem` and `_PytestTerminalWriter` and passes them to `run_sync` and `reporter` functions.
  Reason: Keeps `sync_engine` and `reporter` testable without a live pytest session or real filesystem.
  Alternatives considered: Direct use of `pathlib` and `config.get_terminal_writer()` inside sync_engine — rejected because it couples orchestration to pytest internals.

  ADR-003: Graceful skip when features directory is absent
  Decision: `pytest_configure` checks `features_root.exists()` before calling `run_sync`; if absent, returns silently.
  Reason: Matches AC `@id:d0f2866d` — pytest must complete without errors when the features directory does not exist.
  Alternatives considered: Raising an error — rejected per AC.

  ### Build Changes (needs PO approval: no)
  - No new runtime dependencies beyond `libcst` (already added for stub_writer).

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