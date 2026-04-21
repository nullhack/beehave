Feature: Test stub creation
  Creates top-level test functions for each new Example in backlog and in-progress features.
  Stubs include a skip marker and a verbatim step docstring. Completed features are never touched
  by stub sync.

  Status: BASELINED (2026-04-18)

  Rules (Business):
  - Feature files are parsed using gherkin-official AST — no regex/string manipulation
  - Only `backlog/` and `in-progress/` feature folders receive stub creation
  - `completed/` features are never touched by stub sync
  - New stubs receive `@pytest.mark.skip(reason="not yet implemented")` — stub-sync owns this marker; developer never adds or removes it
  - The docstring includes EVERY step line in order, including `And` and `But` continuations
  - Docstring format per step: `<Keyword>: <step text>` (e.g., `Given: user is logged in`, `And: user has admin role`)
  - Test function bodies start with `raise NotImplementedError` — no section comments
  - Features with `Rule:` blocks: stubs are top-level functions in `<rule_slug>_test.py`
  - Features with no `Rule:` blocks: stubs are module-level functions in `examples_test.py`
  - Feature-level `Background:` → `conftest.py` autouse fixture; Rule-level `Background:` → module-level autouse fixture in `<rule_slug>_test.py`

  Constraints:
  - Must handle the case where the test file does not yet exist (create it)
  - Must handle the case where a test file exists but is missing some stubs (add only the missing ones)
  - Function naming: `test_<feature_slug>_<@id>` — always

  Rule: New stub generation
    As a developer
    I want a test stub to be created for each new Example in backlog and in-progress features
    So that I have a failing test ready to implement for every acceptance criterion

    @id:692972dd
    Example: New stub is created with the correct function name
      Given a backlog feature folder containing a .feature file with a new @id-tagged Example
      When pytest is invoked
      Then a test function named test_<feature_slug>_<@id> exists in the corresponding test file

    @deprecated
    @id:d14d975f
    Example: New stub has no default pytest marker
      Given a backlog feature folder containing a .feature file with a new @id-tagged Example
      When pytest is invoked
      Then the generated test function has no @pytest.mark decorator

    @id:a4c781f2
    Example: New stub has skip marker not yet implemented
      Given a backlog feature folder containing a .feature file with a new @id-tagged Example
      When pytest is invoked
      Then the generated test function has @pytest.mark.skip(reason="not yet implemented") applied

    @deprecated
    @id:e2b093d1
    Example: New stub for a Rule block is a method inside the rule class
      Given a backlog feature file with a Rule block containing a new @id-tagged Example
      When pytest is invoked
      Then the generated stub is a method inside class Test<RuleSlug> in <rule_slug>_test.py

    @deprecated
    @id:c3a8f291
    Example: New stub for a Rule block is a top-level function (not a class method)
      Given a backlog feature file with a Rule block containing a new @id-tagged Example
      When pytest is invoked
      Then the generated stub is a top-level function in <rule_slug>_test.py with no class wrapping

    @id:f1a5c823
    Example: New stub for a feature with no Rule blocks is a module-level function
      Given a backlog feature file with no Rule blocks containing a new @id-tagged Example
      When pytest is invoked
      Then the generated stub is a module-level function in examples_test.py

    @id:777a9638
    Example: New stub body contains raise NotImplementedError
      Given a backlog feature folder containing a .feature file with a new @id-tagged Example
      When pytest is invoked
      Then the generated test function body ends with raise NotImplementedError

    @id:bba184c0
    Example: New stub body contains only raise NotImplementedError with no section comments
      Given a backlog feature folder containing a .feature file with a new @id-tagged Example
      When pytest is invoked
      Then the generated test function body contains no "# Given", "# When", or "# Then" comment lines

    @id:edc964fc
    Example: Test directory uses underscore slug not kebab-case
      Given a backlog feature folder whose name contains hyphens (e.g. "my-feature")
      When pytest is invoked
      Then the test file is created at tests/features/my_feature/ not tests/features/my-feature/

    @id:38d864b9
    Example: Stubs are not created for completed feature Examples
      Given a completed feature folder containing a .feature file with a new @id-tagged Example
      When pytest is invoked
      Then no new test stub is created for that Example

    @bug
    @id:f3e1a290
    Example: Scenario Outline produces a parametrized stub
      Given a backlog feature file containing a Scenario Outline with an Examples table
      When pytest is invoked
      Then a single @pytest.mark.parametrize test stub is created for that Scenario Outline with the Examples table rows as parameter values

  Rule: Docstring generation
    As a developer
    I want the stub docstring to contain all the steps from the Example
    So that the test intent is clear from the code

    @id:db596443
    Example: And and But steps use their literal keyword in the docstring
      Given a backlog feature with an Example containing And and But steps
      When pytest is invoked
      Then each And step appears as "And: <text>" and each But step appears as "But: <text>" in the docstring

    @id:17b01d7a
    Example: Asterisk steps appear as "* <text>" in the docstring
      Given a backlog feature with an Example containing a step written with the * bullet
      When pytest is invoked
      Then that step appears as "*: <text>" in the generated test stub docstring

    @id:c56883ce
    Example: Multi-line doc string attached to a step is included in the docstring
      Given a backlog feature with an Example where a step has an attached multi-line doc string block
      When pytest is invoked
      Then the generated test stub docstring includes the doc string content indented below the step line

    @id:2fc458f8
    Example: Data table attached to a step is included in the docstring
      Given a backlog feature with an Example where a step has an attached data table
      When pytest is invoked
      Then the generated test stub docstring includes the table rows indented below the step line

    @id:7f91cf3a
    Example: Background steps appear as separate Background sections before scenario steps
      Given a backlog feature with a feature-level Background and a Rule-level Background
      When pytest is invoked
      Then the generated test stub docstring contains two "Background:" sections in order before the scenario steps

    @id:9a4e199a
    Example: Scenario Outline stub uses raw template text and includes the Examples table
      Given a backlog feature containing a Scenario Outline with placeholder values and an Examples table
      When pytest is invoked
      Then the generated test stub docstring contains the raw template step text followed by the Examples table

    @bug
    @id:e5c3b271
    Example: Background steps are separated from scenario steps by a blank line in the docstring
      Given a backlog feature with a Background section and a Scenario with its own steps
      When pytest is invoked and the stub is created
      Then the generated test stub docstring contains a blank line between the last Background step and the first Scenario step
