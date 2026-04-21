Feature: Report Steps

  Surfaces BDD acceptance criteria in two output channels: the terminal (at -v or above) and
  pytest-html reports (when pytest-html is installed). Both channels are independently
  configurable via pyproject.toml and are scoped exclusively to tests under tests/features/.

  Status: BASELINED (2026-04-18)

  Rules (Business):
  - Steps are always rendered verbatim from the test docstring — no reformatting
  - Both output channels are scoped exclusively to tests/features/
  - Steps are rendered regardless of test outcome (pass, fail, skip, error)
  - The HTML channel is silently absent when pytest-html is not installed

  Constraints:
  - show_steps_in_terminal defaults to true; active at -v or above
  - show_steps_in_html defaults to true; only active when pytest-html is installed
  - Both features are wired into the single existing pytest_configure entry point
  - pytest-html is an optional install extra: pip install pytest-beehave[html]

  Rule: Terminal Steps Display
    As a developer running pytest with verbosity
    I want BDD steps printed below each feature test result
    So that I can see what each test covers without opening the feature file

    @id:2ba9da81
    Example: Steps appear below test path at -v
      Given a test in tests/features/ with a docstring containing BDD steps
      When pytest runs with -v
      Then the docstring is printed verbatim on the line below the test path followed by a blank line

    @id:0869902b
    Example: Steps appear for skipped stubs at -v
      Given a test in tests/features/ marked skip with a docstring
      When pytest runs with -v
      Then the docstring is printed verbatim below the skipped test path followed by a blank line

    @id:99cbca75
    Example: No steps output for tests outside tests/features/
      Given a test in tests/unit/ with a docstring
      When pytest runs with -v
      Then no additional output is printed for that test

    @id:3c1b6d21
    Example: No steps output when show_steps_in_terminal is false
      Given show_steps_in_terminal = false in pyproject.toml
      And a test in tests/features/ with a docstring
      When pytest runs with -v
      Then no steps are printed for that test

    @id:3278cf4d
    Example: No steps output below -v verbosity
      Given show_steps_in_terminal = true in pyproject.toml
      And a test in tests/features/ with a docstring
      When pytest runs without any -v flag
      Then no steps are printed for that test

  Rule: HTML Acceptance Criteria Column
    As a developer reading a pytest-html report
    I want a dedicated column showing BDD steps for feature tests
    So that the report communicates what each test was verifying

    @id:88d58f5c
    Example: Acceptance Criteria column shows docstring for feature tests
      Given pytest-html is installed and show_steps_in_html = true
      And a test in tests/features/ with a docstring
      When the pytest-html report is generated
      Then the "Acceptance Criteria" column contains the verbatim docstring for that test

    @id:73c4a71a
    Example: Acceptance Criteria column is blank for non-feature tests
      Given pytest-html is installed and show_steps_in_html = true
      And a test outside tests/features/
      When the pytest-html report is generated
      Then the "Acceptance Criteria" column is blank for that test

    @id:6c592c81
    Example: HTML column absent when pytest-html not installed
      Given pytest-html is not installed
      When pytest runs and generates output
      Then no "Acceptance Criteria" column appears and no error is raised
