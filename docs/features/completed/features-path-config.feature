Feature: Features path configuration

  Discovery:

  Status: BASELINED

  Entities:
  | Type | Name | Candidate Class/Method | In Scope |
  |------|------|----------------------|----------|
  | Noun | features folder path | path to `docs/features/` directory | Yes |
  | Noun | `pyproject.toml` | project configuration file | Yes |
  | Noun | `[tool.beehave]` section | configuration section in `pyproject.toml` | Yes |
  | Noun | default path | `docs/features/` relative to project root | Yes |
  | Verb | read config | parse `[tool.beehave]` from `pyproject.toml` | Yes |
  | Verb | resolve path | make the configured path absolute relative to project root | Yes |
  | Verb | fall back to default | use `docs/features/` if no config present | Yes |

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

  Questions:
  | ID | Question | Answer | Status |
  |----|----------|--------|--------|
  | Q1 | What is the exact config key name? | `features_path` under `[tool.beehave]` | ANSWERED |
  | Q2 | Should an invalid/missing configured path be a hard error or a warning? | Hard error — if the user explicitly configured a path that doesn't exist, fail loudly | ANSWERED |

  All questions answered. Discovery frozen.

  Architecture:

  ### Module Structure
  - `pytest_beehave/config.py` — `BeehaveConfig` frozen dataclass (features_path: Path) + `read_config(project_root: Path) -> BeehaveConfig` function
    - `read_config` reads `pyproject.toml` via stdlib `tomllib`, extracts `[tool.beehave].features_path`, resolves it relative to `project_root`, and returns a `BeehaveConfig`
    - Falls back to `project_root / "docs/features"` when `pyproject.toml` is absent or `[tool.beehave]` section is missing
    - Raises `FileNotFoundError` with a descriptive message when `features_path` is explicitly configured but the directory does not exist

  ### Key Decisions
  ADR-001: Use stdlib tomllib (Python 3.11+) instead of a third-party TOML library
  Decision: Use `tomllib` from the standard library (Python ≥ 3.11)
  Reason: No new runtime dependency needed; project already requires Python ≥ 3.13
  Alternatives considered: `tomli` (backport) — rejected because Python 3.13 is already required

  ADR-002: BeehaveConfig as a frozen dataclass, not a plain dict
  Decision: `@dataclass(frozen=True, slots=True)` with a single `features_path: Path` field
  Reason: Typed, immutable, and easy to extend with future config keys without changing callers
  Alternatives considered: returning a raw `Path` — rejected because it cannot be extended without breaking callers

  ADR-003: `read_config` takes `project_root: Path` as a parameter (not auto-detected)
  Decision: Caller supplies the project root; `read_config` does not walk the filesystem to find it
  Reason: Keeps the function pure and testable without filesystem side effects; the plugin hook will supply the root
  Alternatives considered: auto-detect by walking up from `cwd` — rejected because it couples the function to the process environment

  ### Build Changes (needs PO approval: no)
  - No new runtime dependencies — `tomllib` is stdlib in Python 3.11+

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
