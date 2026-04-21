Feature: Cache management — incremental sync cache

  Beehave maintains a `.beehave_cache/features.json` file that stores content
  hashes of `.feature` files and generated stubs. On subsequent `sync` invocations,
  the cache allows beehave to skip unchanged files, making the tool fast enough
  for frequent developer use.

  The cache is not user-visible in normal operation: it auto-rebuilds silently if
  stale, missing, or corrupted. `beehave nest` adds `.beehave_cache/` to
  `.gitignore` automatically so the cache is never accidentally committed.

  Status: BASELINED (2026-04-21)
