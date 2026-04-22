Feature: parameter-handling — Scenario Outline parametrization

  When a .feature file contains a Scenario Outline, beehave generates a parametrized stub using
  the active adapter's parametrize template. The columns table becomes the parametrize arguments.
  If columns change after the initial stub is created, beehave warns and flags the stub as
  requiring manual intervention — it never auto-modifies the parametrize decorator.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - A Scenario Outline stub is created with the adapter's parametrize template on first sync
  - Column changes after initial creation produce a warning only; beehave does not touch the stub

  Constraints:
  - "Column change" means any addition, removal, or rename of an Examples table column

  Rule: Parametrized stub creation
    As a developer
    I want beehave to generate a parametrized stub for each Scenario Outline
    So that my test suite reflects all parameter combinations without manual setup

    @id:9e373760
    Example: Scenario Outline produces a parametrized stub on first sync
      Given a .feature file with a Scenario Outline with columns "input" and "expected"
      When beehave sync creates the stub with the pytest adapter
      Then the stub is decorated with @pytest.mark.parametrize("input, expected", [...]) containing the table values

    @id:21be53b0
    Example: Each row in the Examples table becomes a parametrize entry
      Given a Scenario Outline with an Examples table of three rows
      When beehave sync creates the stub
      Then the parametrize decorator contains exactly three parameter tuples

  Rule: Column change warning
    As a developer
    I want beehave to warn me when Scenario Outline columns change after the stub was created
    So that I know to update the parametrize decorator manually

    @id:e75ff75a
    Example: Adding a column after initial stub creation produces a warning
      Given a parametrized stub already exists for a Scenario Outline
      When a new column is added to the Examples table and beehave sync runs
      Then beehave emits a warning identifying the affected stub and does not modify the parametrize decorator

    @id:4ee36ecb
    Example: Removing a column after initial stub creation produces a warning
      Given a parametrized stub already exists for a Scenario Outline
      When a column is removed from the Examples table and beehave sync runs
      Then beehave emits a warning identifying the affected stub and does not modify the parametrize decorator

    @id:da379195
    Example: Renaming a column after initial stub creation produces a warning
      Given a parametrized stub already exists for a Scenario Outline
      When a column is renamed in the Examples table and beehave sync runs
      Then beehave emits a warning identifying the affected stub and does not modify the parametrize decorator

  Rule: Row-only changes do not warn
    As a developer
    I want beehave to update stub parameter values silently when only row data changes
    So that adding new test cases to an Outline does not require manual intervention

    @id:26570a93
    Example: Adding a row to the Examples table updates the parametrize values without warning
      Given a parametrized stub already exists for a Scenario Outline with two rows
      When a third row is added to the Examples table and beehave sync runs
      Then the parametrize decorator is updated to include the new row and no warning is emitted
