Feature: Sync-Update — update existing test stubs when `.feature` files change

  As a developer refining acceptance criteria,
  I want beehave to refresh the auto-generated parts of existing test stubs when
    the corresponding `.feature` Example changes,
  so that my tests stay in sync with living documentation without losing my
    implementation code.

  Beehave NEVER modifies the test body. When an Example changes, beehave updates
  only the following auto-generated parts:

  1. **Docstring** — re-rendered to match the new Gherkin steps verbatim.
  2. **Function name** — updated if the feature slug changed (i.e. the `.feature`
     file was renamed).
  3. **`@deprecated` marker** — added or removed based on the presence of the
     Gherkin `@deprecated` tag on the Example.

  When a Scenario Outline's column set changes after the initial stub was created,
  beehave emits a warning and flags the stub as "manual intervention required."
  It does NOT update the parametrize decorator or the function signature.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - The test body is sacred: beehave must never delete, insert, or alter anything
    between the function signature and the closing line.
  - ID-based matching is used to pair stubs with Examples; if a match is
    ambiguous, emit a warning and skip.

  Constraints:
  - When a `.feature` file is renamed, the original test directory is left in
    place until the developer decides to delete it.

  Rule: Refresh docstring on step changes
    As a developer changing acceptance criteria wording
    I want the test docstring to stay in sync with the `.feature` file
    So that traceability is preserved

    @id:d0e1f2a3
    Example: Updated steps reflected in docstring
      Given a `.feature` Example whose steps have changed
        and a matching test stub with an outdated docstring
      When beehave sync runs
      Then the test stub's docstring is rewritten to match the new steps verbatim

    @id:e1f2a3b4
    Example: New steps added to existing Example
      Given a `.feature` Example with a new `And` step inserted in the middle
      When beehave sync runs
      Then the test stub's docstring gains that step in exactly the same position

  Rule: Rename function when feature slug changes
    As a developer renaming a `.feature` file
    I want the test function names to follow the new slug automatically
    So that naming stays consistent

    @id:f2a3b4c5
    Example: Feature renamed from login to sign-in
      Given a `.feature` file previously named `login.feature` renamed to
        `sign-in.feature` with the same `@id` tags
      When beehave sync runs
      Then test functions `test_login_<id>` are renamed to `test_sign_in_<id>`
        without changing their bodies

    @id:a3b4c5d6
    Example: Feature slug change with custom naming convention
      Given a project where the adapter uses a custom prefix `bdd_test_`
      When beehave sync renames functions after a feature rename
      Then the prefix `bdd_test_` is preserved and only the slug portion changes

  Rule: Propagate @deprecated tag to adapter marker
    As a developer marking scenarios as deprecated
    I want the corresponding stubs to be tagged with the framework's deprecation
      marker automatically
    So that my test runner handles them appropriately

    @id:b4c5d6e7
    Example: Add deprecated marker to existing stub
      Given a `.feature` Example newly tagged with `@deprecated`
        and a matching test stub without a deprecation marker
      When beehave sync runs
      Then the stub receives the adapter's deprecation marker (e.g.
        `@pytest.mark.deprecated`) while the body remains unchanged

    @id:c5d6e7f8
    Example: Remove deprecated marker when tag is removed
      Given a `.feature` Example where the `@deprecated` tag has been removed
        and a matching test stub with a deprecation marker
      When beehave sync runs
      Then the deprecation marker is removed from the stub

  Rule: Warn on unsupported changes
    As a developer changing Scenario Outline columns
    I want beehave to tell me that it cannot safely update the parametrize
      declaration
    So that I know manual intervention is required

    @id:d6e7f8a9
    Example: Column added to Scenario Outline
      Given a Scenario Outline where a new column `age` was added to the
        `Examples:` table after the stub was first generated
      When beehave sync runs
      Then a warning is emitted naming the test file and the affected `@id`,
        and the stub is left untouched
