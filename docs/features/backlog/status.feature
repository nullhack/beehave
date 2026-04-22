Feature: status — dry-run preview of sync changes

  Shows a summary of what beehave sync would change, without modifying any file. Intended for
  developer review before committing and for CI pipeline gating. Exits 0 when everything is in
  sync and 1 when changes are pending, following Unix convention.

  Status: ELICITING

  Rules (Business):
  - status never writes to any file
  - Exit code 0 means fully in sync; exit code 1 means changes pending

  Constraints:
  - Supports --verbose (human-readable) and --json (machine-readable) output modes
  - Silent by default (Unix philosophy)
