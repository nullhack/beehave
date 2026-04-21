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
