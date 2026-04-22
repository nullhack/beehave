Feature: cache-management — incremental sync cache

  Maintains a JSON cache at .beehave_cache/features.json to track the last-known state of every
  .feature file. On each sync, only changed files are fully reprocessed, keeping sync fast on
  large projects. The cache is invisible in normal operation and never committed to version control.

  Status: ELICITING

  Rules (Business):
  - Cache is auto-created on first sync and updated incrementally on every subsequent sync
  - A missing, stale, or corrupted cache is rebuilt silently without surfacing an error to the user

  Constraints:
  - Cache file is added to .gitignore by beehave nest
  - Cache is not a user-visible artifact
