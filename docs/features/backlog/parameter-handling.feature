Feature: parameter-handling — Scenario Outline parametrization

  When a .feature file contains a Scenario Outline, beehave generates a parametrized stub using
  the active adapter's parametrize template. The columns table becomes the parametrize arguments.
  If columns change after the initial stub is created, beehave warns and flags the stub as
  requiring manual intervention — it never auto-modifies the parametrize decorator.

  Status: ELICITING

  Rules (Business):
  - A Scenario Outline stub is created with the adapter's parametrize template on first sync
  - Column changes after initial creation produce a warning only; beehave does not touch the stub

  Constraints:
  - "Column change" means any addition, removal, or rename of an Examples table column
