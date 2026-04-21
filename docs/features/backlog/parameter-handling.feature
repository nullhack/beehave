Feature: Parameter handling — manage parametrized stubs from Scenario Outlines

  Scenario Outlines with `Examples:` tables generate parametrized test stubs
  rather than flat functions. The adapter renders the stub using its own
  parametrize template (e.g. `@pytest.mark.parametrize(...)` for pytest) so
  that parameters are handled idiomatically for the target test runner.

  When a Scenario Outline's column set changes after the initial stub was created,
  beehave emits a warning and flags the stub as "manual intervention required."
  Beehave does NOT update the parametrize decorator or the function signature —
  the developer must update these manually.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - Each row in the `Examples:` table produces one call of the parametrized test.
  - Column headers become parameter names in the function signature.
  - The adapter controls the exact syntax of the parametrize declaration.

  Constraints:
  - Changes to the `Examples:` table (adding/removing rows) do not trigger
    stub regeneration; new or removed rows are handled by the test runner's
    parametrize mechanism automatically.

  Rule: Generate parametrized stubs from Scenario Outlines
    As a developer writing data-driven scenarios
    I want beehave to generate a native parametrize declaration
    So that each row of the Examples table becomes a distinct test invocation

    @id:b8c9d0e1
    Example: Two-column Scenario Outline with two rows
      Given a `.feature` Scenario Outline with columns `name` and `email`
        and two example rows
      When beehave sync runs
      Then the generated function has parameters `(name, email)` and a
        parametrize declaration supplied by the adapter covering both rows

    @id:c9d0e1f2
    Example: Scenario Outline with embedded replacement markers
      Given a `.feature` Scenario Outline where step text contains `<name>`
      When beehave sync runs
      Then the docstring shows the unsubstituted step text with `<name>`
        preserved, while the parametrize declaration maps the column `name`

  Rule: Warn on column schema changes
    As a developer changing Scenario Outline columns
    I want beehave to flag that the parametrize declaration is stale
    So that I know to update it manually

    @id:d0e1f2a3
    Example: Column renamed after stub generation
      Given a `.feature` Scenario Outline where the column `name` was renamed
        to `username` after the parametrized stub was created
      When beehave sync runs
      Then a warning is emitted naming the file, the affected `@id`, and the
        column change

    @id:e1f2a3b4
    Example: Column added after stub generation
      Given a `.feature` Scenario Outline where a new column `age` was added
        after the parametrized stub was created
      When beehave sync runs
      Then a warning is emitted naming the file, the affected `@id`, and the
        column addition
