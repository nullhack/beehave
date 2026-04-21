Feature: Stub format configuration

  Controls the output format of generated test stubs via a `stub_format` key in
  `[tool.beehave]` in `pyproject.toml`. Two formats are supported: `"functions"`
  (default) generates top-level functions in `<rule_slug>_test.py` with no class
  wrapper; `"classes"` generates stubs as methods inside `class Test<RuleSlug>`.
  When the key is absent, `"functions"` is used. Existing projects that relied on
  the class-based output can opt back in by setting `stub_format = "classes"`.

  Status: BASELINED (2026-04-19)

  Rules (Business):
  - `stub_format` lives under `[tool.beehave]` in `pyproject.toml`
  - Valid values are exactly `"functions"` and `"classes"` (case-sensitive)
  - Default when key is absent: `"functions"`
  - Features with no `Rule:` blocks always produce module-level functions in `examples_test.py` regardless of `stub_format`
  - The format setting applies to ALL Rule-block features in the project uniformly

  Constraints:
  - Invalid `stub_format` values must produce a hard error at pytest startup (not silently ignored)
  - Changing `stub_format` does not retroactively reformat existing stubs — only new stubs are affected

  Rule: Default format selection
    As a developer
    I want stub generation to default to top-level functions when no stub_format is configured
    So that new projects and existing projects without explicit configuration get the preferred format automatically

    @id:a1b2c3d4
    Example: Stub is a top-level function when stub_format is absent
      Given a pyproject.toml with no stub_format key under [tool.beehave]
      When pytest generates a stub for a Rule-block Example
      Then the stub is a top-level function def test_<feature_slug>_<@id> with no class wrapper

    @id:b2c3d4e5
    Example: Absent stub_format does not raise an error
      Given a pyproject.toml with no stub_format key under [tool.beehave]
      When pytest starts up
      Then pytest starts without any stub_format-related error

  Rule: Explicit functions format
    As a developer
    I want to explicitly set stub_format = "functions" in pyproject.toml
    So that I can document my format choice and ensure top-level function stubs are generated

    @id:f1e2d3c4
    Example: Stub is a top-level function when stub_format = "functions"
      Given a pyproject.toml with stub_format = "functions" under [tool.beehave]
      When pytest generates a stub for a Rule-block Example
      Then the stub is a top-level function def test_<feature_slug>_<@id> with no class wrapper

  Rule: Classes format selection
    As a developer
    I want to set stub_format = "classes" in pyproject.toml
    So that I can restore the class-wrapped stub output for projects that prefer that style

    @id:a2b3c4d5
    Example: Stub is a class method when stub_format = "classes"
      Given a pyproject.toml with stub_format = "classes" under [tool.beehave]
      When pytest generates a stub for a Rule-block Example
      Then the stub is a method inside class Test<RuleSlug> in <rule_slug>_test.py

    @id:b3c4d5e6
    Example: Class name is derived from the Rule title slug
      Given a pyproject.toml with stub_format = "classes" and a Rule titled "Wall bounce"
      When pytest generates a stub for an Example under that Rule
      Then the stub is inside a class named TestWallBounce

  Rule: Invalid format rejection
    As a developer
    I want pytest to fail immediately with a clear error when stub_format has an unrecognised value
    So that misconfiguration is caught at startup rather than silently producing wrong output

    @id:f6a7b8c9
    Example: Pytest fails at startup when stub_format has an unrecognised value
      Given a pyproject.toml with stub_format = "methods" under [tool.beehave]
      When pytest starts up
      Then pytest exits with a non-zero status and an error message naming the invalid value

  Rule: No-Rule feature unaffected
    As a developer
    I want features with no Rule blocks to always produce module-level functions in examples_test.py
    So that the stub_format setting does not change the behavior of no-Rule features

    @id:a7b8c9d0
    Example: No-Rule feature produces module-level functions regardless of stub_format = "classes"
      Given a pyproject.toml with stub_format = "classes" under [tool.beehave]
      And a feature file with no Rule blocks
      When pytest generates stubs for that feature
      Then the stubs are module-level functions in examples_test.py with no class wrapper
