Feature: Status — dry-run preview of sync changes
Status: BASELINED (2026-04-23)

`beehave status` previews what `beehave sync` would change without modifying
any files. It follows the Unix CI contract: exit 0 if in sync, exit 1 if
changes are pending.

Rule: Status reports sync state

  @id:cc96c609
  Example: Project is in sync
    Given a project where all stubs match their `.feature` files
    When the user runs "beehave status"
    Then the command outputs "OK"
    And the exit code is 0

  @id:80e23cea
  Example: Project has pending changes
    Given a project where stubs are out of date with `.feature` files
    When the user runs "beehave status"
    Then a summary of what would change is available
    And the exit code is 1

Rule: Status supports output formats

  @id:91d8ac98
  Example: Verbose output for human reading
    Given a project with pending changes
    When the user runs "beehave status --verbose"
    Then human-readable details of each pending change are shown

  @id:01434077
  Example: JSON output for machine reading
    Given a project with pending changes
    When the user runs "beehave status --json"
    Then machine-readable JSON output is produced
