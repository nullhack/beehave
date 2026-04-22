Feature: adapter-contract — common framework adapter interface

  Defines the interface that all framework adapters must implement so that beehave's core can
  generate correctly-formatted stubs for any supported test framework. The active adapter is
  selected by the framework config key or the --framework CLI flag. In v1 only the built-in
  pytest adapter exists; the interface is designed to allow third-party adapters in future.

  Status: ELICITING

  Rules (Business):
  - The active adapter is selected by the framework key in [tool.beehave] or --framework flag
  - Default adapter is pytest when neither config nor flag is set

  Constraints:
  - Every adapter must supply: skip marker, deprecated marker, parametrize template, stub file header
  - v1: only built-in adapters; third-party adapter registration is out of v1 scope
