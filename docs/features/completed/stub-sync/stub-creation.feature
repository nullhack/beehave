Feature: Test stub creation
  As a developer
  I want a test stub to be created for each new Example in backlog and in-progress features
  So that I have a failing test ready to implement for every acceptance criterion

  @id:692972dd
  Example: New stub is created with the correct function name
    Given a backlog feature folder containing a .feature file with a new @id-tagged Example
    When pytest is invoked
    Then a test function named test_<feature_slug>_<id_hex> exists in the corresponding test file

  @id:d14d975f
  Example: New stub has no default pytest marker
    Given a backlog feature folder containing a .feature file with a new @id-tagged Example
    When pytest is invoked
    Then the generated test function has no @pytest.mark decorator

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
