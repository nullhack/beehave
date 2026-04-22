Feature: status — dry-run preview of sync changes

  Shows a summary of what beehave sync would change, without modifying any file. Intended for
  developer review before committing and for CI pipeline gating. Exits 0 when everything is in
  sync and 1 when changes are pending, following Unix convention.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - status never writes to any file
  - Exit code 0 means fully in sync; exit code 1 means changes pending

  Constraints:
  - Supports --verbose (human-readable) and --json (machine-readable) output modes
  - Silent by default (Unix philosophy)

  Rule: Read-only guarantee
    As a developer
    I want beehave status to never modify any file
    So that I can safely run it in CI without fear of unintended side effects

    @id:525cf08b
    Example: No files are written when status runs
      Given a project with unsynced .feature files
      When beehave status runs
      Then no files in the project are created, modified, or deleted

    @id:fa7a30b2
    Example: Status reports what sync would do without doing it
      Given a project with one new Example that has no stub
      When beehave status runs
      Then the output lists the missing stub and exit code is 1

  Rule: Exit code contract
    As a developer
    I want beehave status to exit 0 when in sync and 1 when changes are pending
    So that CI pipelines can gate on sync state without parsing output

    @id:2e14c727
    Example: Exit code is 0 when project is fully in sync
      Given a project where all Examples have corresponding stubs and all stubs match their Examples
      When beehave status runs
      Then the exit code is 0

    @id:08ba37c8
    Example: Exit code is 1 when a new stub needs to be created
      Given a project with at least one Example that has no corresponding stub
      When beehave status runs
      Then the exit code is 1

    @id:53fd3157
    Example: Exit code is 1 when a stub docstring is out of date
      Given a project where an Example's step text has changed since the stub was generated
      When beehave status runs
      Then the exit code is 1

  Rule: Output modes
    As a developer
    I want to choose between silent, verbose, and JSON output
    So that I can use status both interactively and in automated pipelines

    @id:f2bce539
    Example: Default output is silent when project is in sync
      Given a fully synced project
      When beehave status runs with no output flags
      Then nothing is written to stdout or stderr

    @id:6bc2555f
    Example: --verbose output lists each pending change in human-readable form
      Given a project with two pending changes
      When beehave status --verbose runs
      Then stdout contains one human-readable line per pending change

    @id:b9301030
    Example: --json output emits a machine-readable JSON object
      Given a project with pending changes
      When beehave status --json runs
      Then stdout is valid JSON describing the pending changes
