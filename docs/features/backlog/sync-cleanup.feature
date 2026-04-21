Feature: Sync-Cleanup — handle orphaned test stubs when `.feature` files are deleted

  As a developer cleaning up obsolete scenarios,
  I want beehave to detect test stubs whose `@id` no longer exists in any
  `.feature` file and warn me about the orphan,
  so that my test suite does not accumulate dead code.

  An orphan is triggered when the `@id` embedded in a test function name has no
  matching `@id` in any `.feature` file across the project. Beehave warns only —
  it leaves the stub completely unchanged. The developer deletes orphans manually.

  When a `.feature` file is deleted, beehave warns only (C5 behavior). The
  corresponding test stubs become orphans and are surfaced by orphan detection.

  When a feature is renamed (slug changes but IDs still match), beehave renames
  the test function to match the new slug while preserving the body. This is
  sync-update territory, not cleanup.

  When a test stub is in the wrong location (IDs match but path is incorrect),
  beehave moves the test function/file to the correct location, preserving the body.

  Status: BASELINED (2026-04-21)
