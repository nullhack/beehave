Feature: Status — dry-run preview of sync changes

  `beehave status` performs the same analysis as `sync` but makes no changes.
  It reports a summary of what would be created, updated, or warned about if
  `beehave sync` were run, allowing developers and CI pipelines to review the
  impact before committing to a sync.

  Output follows the standard CLI output contract: silent by default (exits 0 if
  everything is in sync, exits 1 if changes are pending), `--verbose` for
  human-readable detail, and `--json` for machine-readable output. The exit code
  contract makes `beehave status` directly usable as a CI gate.

  `beehave status` also serves as the dry-run/preview mode for id-generation —
  there is no separate preview flag for that operation.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - `status` never writes to disk.
  - Exit code is the only unreliable signal in silent mode: 0 means "in sync",
    non-zero means "changes pending".

  Constraints:
  - Must run in less than 5 seconds for projects with ≤ 100 `.feature` files.

  Rule: Preview sync impact without changing files
    As a developer reviewing changes before committing
    I want to see what `sync` would do without actually doing it
    So that I can decide whether to run sync or manually adjust things first

    @id:e9f0a1b2
    Example: In-sync project exits 0 silently
      Given a project where every `.feature` Example has a matching test stub
      When I run `beehave status`
      Then the command exits 0 and produces no output

    @id:f0a1b2c3
    Example: New features reported in verbose mode
      Given a project with a new `.feature` file containing untagged Examples
      When I run `beehave status --verbose`
      Then the output lists the new stubs that would be created and the IDs
        that would be assigned

    @id:a1b2c3d4
    Example: Out-of-sync project exits 1
      Given a project where a `.feature` file was deleted and orphans remain
      When I run `beehave status`
      Then the command exits 1

  Rule: Emit machine-readable output for CI
    As a CI pipeline maintainer
    I want structured output I can parse
    So that I can gate builds on beehave alignment

    @id:b2c3d4e5
    Example: JSON output shows counts and file list
      Given a project with pending stub creations and orphan warnings
      When I run `beehave status --json`
      Then the output is valid JSON containing counts for create, update, and
        warn actions, plus a list of affected files

    @id:c3d4e5f6
    Example: JSON output for in-sync project
      Given a fully aligned project
      When I run `beehave status --json`
      Then the output is valid JSON with all counts equal to zero
