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
