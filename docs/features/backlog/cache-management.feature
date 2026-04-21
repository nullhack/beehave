Feature: Cache management — incremental sync cache

  Beehave maintains a `.beehave_cache/` directory (or similar) that stores
  content hashes of `.feature` files and generated stubs. On subsequent `sync`
  invocations, the cache allows beehave to skip unchanged files, making the
  tool fast enough for frequent developer use.

  Status: DRAFT
