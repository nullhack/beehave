Feature: Import Completeness

  Generated test stubs must import all decorator types they use. When a .feature file contains And or But steps, the generated stub file uses @And and @But decorators but currently omits them from the import line, causing NameError at import time. This feature addresses PP12.

  Rules (Business):
  - When generate() creates a test stub that uses @And or @But decorators, the import line must include And and But
  - When generate() creates a stub with only Given/When/Then decorators, the import line includes only those used
  - The import line must always produce syntactically valid, importable Python

  Constraints:
  - .feature files are the source of truth — beehave never modifies step text in .feature files
  - Import completeness (QA12): when generate() creates stubs with And/But decorators, those names are importable
  - No NameError at import time; pytest can collect the file
  - MoSCoW: Must

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP12 — Import completeness for And/But decorators in generated stubs |

  Rule: Import line includes all decorator types used in the scenario
    As a property-based TDD developer
    I want generated stubs to import every decorator type they reference
    So that the file is importable without NameError

    @id:f1e2d3c4
    Example: Stub with And step imports And decorator
      Given a .feature file with steps using Given and And keywords
      When beehave generate creates the test stub
      Then the import line includes "And" alongside "Given"
      And the file passes py_compile.compile()

    @id:b5a69788
    Example: Stub with But step imports But decorator
      Given a .feature file with steps using Then and But keywords
      When beehave generate creates the test stub
      Then the import line includes "But" alongside "Then"
      And the file passes py_compile.compile()

    @id:87655926
    Example: Stub with Given/When/Then only does not import And/But
      Given a .feature file with steps using only Given, When, Then keywords
      When beehave generate creates the test stub
      Then the import line includes "Given, When, Then"
      And the import line does not include "And" or "But"

  Rule: Generated stubs are always syntactically valid Python
    As a QA engineer
    I want every generated stub file to pass py_compile.compile()
    So that pytest can always collect the file

    @id:01fe4990
    Example: Stub with all five decorator types is valid Python
      Given a .feature file with steps using Given, When, Then, And, But keywords
      When beehave generate creates the test stub
      Then the import line includes "Given, When, Then, And, But"
      And the file passes py_compile.compile()

    @id:3d5935ce
    Example: Stub with only And steps is valid Python
      Given a .feature file with a scenario containing only And and But steps (following a Given from Background)
      When beehave generate creates the test stub
      Then the import line includes "And, But"
      And the file passes py_compile.compile()
