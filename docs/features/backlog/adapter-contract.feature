Feature: adapter-contract — common framework adapter interface

  Defines the interface that all framework adapters must implement so that beehave's core can
  generate correctly-formatted stubs for any supported test framework. The active adapter is
  selected by the framework config key or the --framework CLI flag. In v1 only the built-in
  pytest adapter exists; the interface is designed to allow third-party adapters in future.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - The active adapter is selected by the framework key in [tool.beehave] or --framework flag
  - Default adapter is pytest when neither config nor flag is set

  Constraints:
  - Every adapter must supply: skip marker, deprecated marker, parametrize template, stub file header
  - v1: only built-in adapters; third-party adapter registration is out of v1 scope

  Rule: Adapter selection
    As a developer
    I want beehave to select the correct adapter based on my configuration
    So that generated stubs match my test framework conventions

    @id:50a73f9c
    Example: pytest adapter is selected when framework = "pytest"
      Given [tool.beehave] with framework = "pytest"
      When beehave resolves the active adapter
      Then the pytest adapter is used for all stub generation

    @id:33d9c4c3
    Example: pytest is the default when no framework is configured
      Given no framework key in [tool.beehave] and no --framework flag
      When beehave resolves the active adapter
      Then the pytest adapter is used

    @id:50e56841
    Example: --framework flag overrides config file adapter
      Given [tool.beehave] with framework = "pytest" and invocation with --framework pytest
      When beehave resolves the active adapter
      Then the pytest adapter is used

    @id:0372d64b
    Example: Unknown framework value raises an error
      Given [tool.beehave] with framework = "unknown_framework"
      When beehave resolves the active adapter
      Then beehave exits with an error naming the unrecognised framework

  Rule: Adapter contract completeness
    As a framework adapter implementor
    I want a clear contract specifying what every adapter must provide
    So that beehave's core can use any adapter without knowing its internals

    @id:ff712870
    Example: Adapter provides a skip marker string
      Given the pytest adapter is active
      When beehave requests the skip marker
      Then it returns a non-empty string usable as a Python decorator

    @id:99582b14
    Example: Adapter provides a deprecated marker string
      Given the pytest adapter is active
      When beehave requests the deprecated marker
      Then it returns a non-empty string usable as a Python decorator

    @id:ddc63c1a
    Example: Adapter provides a parametrize template string
      Given the pytest adapter is active
      When beehave requests the parametrize template
      Then it returns a non-empty string usable as a Python decorator accepting column names and rows

    @id:17e6d732
    Example: Adapter provides a stub file header string
      Given the pytest adapter is active
      When beehave requests the stub file header
      Then it returns a non-empty string valid as the opening lines of a Python test file
