Feature: Features directory bootstrap

  Discovery:

  Status: BASELINED (2026-04-18)

  Entities:
  | Type | Name                  | Candidate Class/Method                          | In Scope |
  |------|-----------------------|-------------------------------------------------|----------|
  | Noun | features directory    | root configured features path (e.g. docs/features/) | Yes  |
  | Noun | backlog subfolder     | docs/features/backlog/                          | Yes      |
  | Noun | in-progress subfolder | docs/features/in-progress/                      | Yes      |
  | Noun | completed subfolder   | docs/features/completed/                        | Yes      |
  | Noun | .feature file         | Gherkin file found directly in the root features dir | Yes |
  | Noun | pytest plugin         | BeehavePlugin                                   | Yes      |
  | Verb | bootstrap             | create missing canonical subfolders             | Yes      |
  | Verb | migrate               | move root-level .feature files to backlog/      | Yes      |
  | Verb | detect                | check whether the three-subfolder structure exists | Yes   |

  Rules (Business):
  - Bootstrap runs as the first action of every pytest invocation, before stub sync
  - Bootstrap only runs if the root features directory exists; if it does not exist, it is skipped
  - All three subfolders (backlog/, in-progress/, completed/) must exist; each missing one is created independently
  - Only .feature files directly in the root features directory (not inside any subfolder) are migrated to backlog/
  - Non-.feature files in the root features directory (e.g. discovery.md) are never moved
  - Files already inside backlog/, in-progress/, or completed/ are never touched by migration
  - Name collision during migration: leave the root-level file in place and emit a warning; do not overwrite
  - If the structure is already correct and no root-level .feature files exist, the bootstrap is a silent no-op

  Constraints:
  - Bootstrap must complete before stub sync begins so that migrated files are available for stub sync in the same run
  - Terminal output style must be consistent with the existing stub sync reporting

  Session 1 — Individual Entity Elicitation:
  | ID | Question | Answer | Status |
  |----|----------|--------|--------|
  | Q1 | What triggers the bootstrap — always on every run, or only when structure is missing? | Always run on every pytest invocation; it is a no-op when structure is already correct | ANSWERED |
  | Q2 | What constitutes "missing structure" — all three subfolders absent, or any one? | Any missing subfolder triggers creation of that subfolder; all three must exist | ANSWERED |
  | Q3 | What if only some subfolders exist? | Create only the missing ones; existing subfolders are not touched | ANSWERED |
  | Q4 | Are only .feature files migrated, or all files? | Only .feature files directly in the root features folder; other files are left in place | ANSWERED |
  | Q5 | What if a root-level .feature file has the same name as one already in backlog/? | Leave the root-level file in place and emit a warning; do not overwrite | ANSWERED |
  | Q6 | Should bootstrap emit terminal output? | Yes — report each action (subfolder created, file moved, collision warning); no output if no-op | ANSWERED |
  | Q7 | What if the root features directory does not exist at all? | Bootstrap is skipped; existing graceful handling in plugin-hook covers this case | ANSWERED |
  | Q8 | Does bootstrap run before or after stub sync? | Bootstrap runs first so migrated files are available for stub sync in the same run | ANSWERED |
  | Q9 | Are non-.feature files in the root features folder migrated? | No — only .feature files are migrated; discovery.md and other files stay in place | ANSWERED |

  Template §1: CONFIRMED
  Synthesis: The bootstrap feature ensures the three-subfolder structure (backlog/, in-progress/,
  completed/) exists inside the configured features directory. It runs as the first action of every
  pytest invocation, before stub sync. If the root features directory exists but any subfolder is
  missing, the plugin creates the missing subfolder(s) independently. Any .feature files found
  directly in the root features directory are moved to backlog/; non-.feature files are not touched.
  Name collisions during migration result in the root-level file being left in place with a warning.
  If the structure is already correct and no root-level .feature files exist, the bootstrap is a
  silent no-op. If the root features directory does not exist, the bootstrap is skipped entirely.

  Session 2 — Cluster / Big Picture:
  | ID | Question | Answer | Status |
  |----|----------|--------|--------|
  | Q10 | Are nested non-canonical subdirectories in the root features folder left alone? | Yes — only the three canonical subfolders are managed; any other subdirectory is ignored | ANSWERED |
  | Q11 | Is the bootstrap idempotent — safe to run multiple times? | Yes — creating an already-existing subfolder is a no-op; migration only moves files not already in a subfolder | ANSWERED |

  Template §2: CONFIRMED
  Clusters:
  - Subfolder creation: When any of backlog/, in-progress/, or completed/ is missing, the plugin creates the missing subfolder(s) and reports each creation to the terminal
  - Feature file migration: Any .feature file found directly in the root features directory is moved to backlog/ and reported to the terminal
  - Migration collision handling: If a root-level .feature file shares a name with an existing backlog/ file, it is left in place and a warning is emitted
  - No-op behavior: If all three subfolders exist and no root-level .feature files are present, the bootstrap completes silently

  Session 3 — Feature Synthesis:
  Synthesis: The features-dir-bootstrap feature ensures the Beehave plugin can always operate on a
  well-structured features directory. When pytest is invoked, the plugin runs a bootstrap step as its
  very first action (before stub sync). The bootstrap inspects the configured features directory and,
  if it exists, ensures all three canonical subfolders (backlog/, in-progress/, completed/) are
  present — creating any that are missing. It then scans for .feature files directly in the root
  features directory (not inside any subfolder) and moves them to backlog/, making them available for
  stub sync in the same pytest run. Non-.feature files in the root are left untouched. If a name
  collision occurs (a root-level .feature file shares a name with an existing backlog/ file), the
  root-level file is left in place and a warning is emitted. If the structure is already correct and
  no root-level .feature files exist, the bootstrap is a complete no-op with no terminal output. If
  the root features directory does not exist, the bootstrap is skipped entirely.
  Template §3: CONFIRMED — stakeholder approved 2026-04-18

  Architecture:

  ### Module Structure
  - `pytest_beehave/bootstrap.py` — `bootstrap_features_directory(features_root: Path) -> BootstrapResult`. `BootstrapResult` frozen dataclass (created_subfolders, migrated_files, collision_warnings) with `is_noop` property. `_CANONICAL_SUBFOLDERS` constant tuple.
  - `pytest_beehave/reporter.py` — `report_bootstrap(writer, result)` — writes bootstrap actions to terminal; no output when `result.is_noop`.
  - `pytest_beehave/plugin.py` — calls `bootstrap_features_directory` before `run_sync`; passes result to `report_bootstrap`.

  ### Key Decisions
  ADR-001: Bootstrap is a pure function of the filesystem state
  Decision: `bootstrap_features_directory` takes only `features_root: Path` and performs all filesystem operations directly via `pathlib`.
  Reason: Bootstrap operations (mkdir, rename) are idempotent and low-risk; no Protocol abstraction needed at this scale.
  Alternatives considered: Injecting a filesystem Protocol — rejected because bootstrap is simple enough that the added indirection is YAGNI.

  ADR-002: BootstrapResult.is_noop drives terminal output
  Decision: `report_bootstrap` produces no output when `result.is_noop` is True.
  Reason: Matches AC `@id:5e6f9b17` — no output when structure is already correct.
  Alternatives considered: Always printing a "bootstrap OK" message — rejected per AC.

  ADR-003: Name collision leaves root-level file in place with a warning
  Decision: When a root-level `.feature` file shares a name with an existing `backlog/` file, `bootstrap_features_directory` records the filename in `collision_warnings` and does not move the file.
  Reason: Matches AC `@id:7f2a0d51` and `@id:8c3b1e96`; prevents data loss.
  Alternatives considered: Overwriting the backlog file — rejected because it loses the existing backlog file.

  ### Build Changes (needs PO approval: no)
  - No new runtime dependencies (uses stdlib `pathlib` only).

  Rule: Subfolder creation
    As a developer
    I want the plugin to create missing canonical subfolders automatically
    So that the features directory structure is always ready for stub sync without manual setup

    @id:3a1f8c2e
    Example: All three subfolders are created when none exist
      Given the features directory exists with no backlog, in-progress, or completed subfolders
      When pytest is invoked
      Then the backlog, in-progress, and completed subfolders all exist inside the features directory

    @id:b7d4e091
    Example: Only the missing subfolders are created when some already exist
      Given the features directory exists with a backlog subfolder but no in-progress or completed subfolders
      When pytest is invoked
      Then the in-progress and completed subfolders are created and the backlog subfolder is unchanged

    @id:c2a53f7d
    Example: Subfolder creation is reported to the terminal
      Given the features directory exists with no backlog, in-progress, or completed subfolders
      When pytest is invoked
      Then the terminal output names each subfolder that was created

  Rule: Feature file migration
    As a developer
    I want .feature files in the root features directory to be moved to backlog automatically
    So that existing feature files are immediately available for stub sync without manual reorganisation

    @id:e8b61d04
    Example: A .feature file in the root features directory is moved to backlog
      Given the features directory contains a .feature file directly (not inside any subfolder)
      When pytest is invoked
      Then that .feature file exists in the backlog subfolder and no longer exists in the root features directory

    @id:f3c97a52
    Example: Non-.feature files in the root features directory are not moved
      Given the features directory contains a non-.feature file (e.g. discovery.md) directly in the root
      When pytest is invoked
      Then that file remains in the root features directory and is not moved to backlog

    @id:a9d02b6e
    Example: Files already inside a subfolder are not moved
      Given the features directory contains a .feature file inside the in-progress subfolder
      When pytest is invoked
      Then that file remains in the in-progress subfolder and is not moved to backlog

    @id:d1e74c83
    Example: Migration is reported to the terminal
      Given the features directory contains a .feature file directly in the root
      When pytest is invoked
      Then the terminal output names the file that was moved to backlog

  Rule: Migration collision handling
    As a developer
    I want to be warned when a root-level .feature file cannot be migrated due to a name conflict
    So that I can resolve the conflict manually without losing either file

    @id:7f2a0d51
    Example: Root-level .feature file is left in place when a same-named file exists in backlog
      Given the features directory contains root-level feature.feature and backlog/feature.feature already exists
      When pytest is invoked
      Then root-level feature.feature is not moved and backlog/feature.feature is unchanged

    @id:8c3b1e96
    Example: A collision warning is emitted to the terminal
      Given the features directory contains root-level feature.feature and backlog/feature.feature already exists
      When pytest is invoked
      Then the terminal output contains a warning naming the conflicting file and its location

  Rule: No-op when structure is correct
    As a developer
    I want the bootstrap to produce no output when the features directory is already well-structured
    So that normal pytest runs are not cluttered with unnecessary messages

    @id:5e6f9b17
    Example: Bootstrap produces no terminal output when structure is already correct
      Given the features directory contains backlog, in-progress, and completed subfolders and no root-level .feature files
      When pytest is invoked
      Then the terminal output contains no bootstrap messages

    @id:2d8a4c70
    Example: Bootstrap is skipped when the features directory does not exist
      Given the features directory does not exist
      When pytest is invoked
      Then pytest completes collection without errors and no bootstrap messages appear in the terminal
