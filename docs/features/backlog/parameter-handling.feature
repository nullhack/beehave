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
