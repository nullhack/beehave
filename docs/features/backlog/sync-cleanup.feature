Feature: Sync-Cleanup — handle orphaned test stubs when `.feature` files are deleted
  As a developer cleaning up obsolete scenarios,
  I want beehave to detect test stubs whose `.feature` file or `@id` no longer exists
  and warn me (or optionally error) about the orphan,
  so that my test suite does not accumulate dead code.
