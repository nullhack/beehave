Feature: Test stub creation
  As a developer
  I want test stubs to be created for each new Example in backlog and in-progress features
  So that I have failing tests ready to implement for every acceptance criterion

  Discovery:

  Status: BASELINED

  Entities:
  | Type | Name | Candidate Class/Method | In Scope |
  |------|------|----------------------|----------|
  | Noun | test stub | generated `test_<feature_slug>_<hex>()` method or function | Yes |
  | Noun | test file | `tests/features/<feature>/<rule_slug>_test.py` or `examples_test.py` | Yes |
  | Noun | feature slug | underscored folder name used in function names | Yes |
  | Noun | rule slug | `Rule:` title slugified (hyphens, lowercase); used as test file name | Yes |
  | Noun | class Test<RuleSlug> | class wrapping all stubs for a Rule block | Yes |
  | Noun | conftest.py | autouse fixture module for feature-level Background steps | Yes |
  | Noun | docstring | step-by-step docstring in test stub | Yes |
  | Noun | step | individual Gherkin step (Given/When/Then/And/But) | Yes |
  | Noun | backlog stage | `docs/features/backlog/` | Yes |
  | Noun | in-progress stage | `docs/features/in-progress/` | Yes |
  | Noun | completed stage | `docs/features/completed/` — excluded from stub sync | Yes |
  | Verb | create stub | write new test method/function for new Example | Yes |
  | Verb | build all-steps docstring | include every step line (Given/When/Then/And/But) | Yes |

  Rules (Business):
  - Feature files are parsed using gherkin-official AST — no regex/string manipulation
  - Only `backlog/` and `in-progress/` feature folders receive stub creation
  - `completed/` features are never touched by stub sync
  - New stubs receive `@pytest.mark.skip(reason="not yet implemented")` — stub-sync owns this marker; developer never adds or removes it
  - The docstring includes EVERY step line in order, including `And` and `But` continuations
  - Docstring format per step: `<Keyword>: <step text>` (e.g., `Given: user is logged in`, `And: user has admin role`)
  - Test function bodies start with `raise NotImplementedError` — no section comments
  - Features with `Rule:` blocks: stubs are methods inside `class Test<RuleSlug>` in `<rule_slug>_test.py`
  - Features with no `Rule:` blocks: stubs are module-level functions in `examples_test.py`
  - Feature-level `Background:` → `conftest.py` autouse fixture; Rule-level `Background:` → module-level autouse fixture in `<rule_slug>_test.py`

  Constraints:
  - Must handle the case where the test file does not yet exist (create it)
  - Must handle the case where a test file exists but is missing some stubs (add only the missing ones)
  - Function naming: `test_<feature_slug>_<id_hex>` — always, whether the stub is a method (inside a class) or a top-level function

  Questions:
  | ID | Question | Answer | Status |
  |----|----------|--------|--------|
  | Q1 | What is the stub body for a newly created test? | `raise NotImplementedError` only — no `# Given`, `# When`, or `# Then` section comments | ANSWERED |
  | Q2 | Should the test file header (module docstring, imports) be preserved on update? | Yes — only the function name, decorators, and docstring are touched; file header is preserved | ANSWERED |

  All questions answered. Discovery frozen.

  Architecture:

  ### Module Structure
  - `pytest_beehave/feature_parser.py` — `parse_feature(path: Path) -> ParsedFeature`; `collect_all_example_ids(feature) -> set[ExampleId]`. `ParsedFeature`, `ParsedRule`, `ParsedExample`, `ParsedStep` frozen dataclasses. `GherkinParserProtocol` Protocol.
  - `pytest_beehave/stub_writer.py` — `build_docstring(feature, rule, example) -> str`; `build_function_name(feature_slug, example_id) -> str`; `build_class_name(rule_slug) -> str`; `write_stub_to_file(path, spec) -> SyncAction`. `StubSpec` frozen dataclass. `SyncAction` frozen dataclass.
  - `pytest_beehave/models.py` — `FeatureSlug`, `RuleSlug`, `FeatureStage` — shared value objects.

  ### Key Decisions
  ADR-001: Use libcst for all test file writes
  Decision: All stub creation and updates use `libcst` to parse and modify Python source trees.
  Reason: Preserves formatting, comments, and existing function bodies; avoids string-template fragility.
  Alternatives considered: String templates / `ast` module — rejected because `ast` cannot round-trip source code with formatting preserved; string templates are fragile.

  ADR-002: Stub body is always `raise NotImplementedError` with no section comments
  Decision: New stubs contain only `raise NotImplementedError` in the body — no `# Given`, `# When`, `# Then` comments.
  Reason: Matches AC Q1 answer; section comments are redundant given the docstring.
  Alternatives considered: Adding section comments — rejected per AC Q1.

  ADR-003: Feature slug uses underscores; rule slug uses hyphens
  Decision: `FeatureSlug` replaces hyphens with underscores (for Python identifiers); `RuleSlug` uses hyphens (for file names).
  Reason: Python function/class names cannot contain hyphens; file names can.
  Alternatives considered: Both using underscores — rejected because file names with underscores diverge from the spec.

  ADR-004: completed/ features never receive new stubs
  Decision: `write_stub_to_file` is never called for features in `FeatureStage.COMPLETED`.
  Reason: Matches AC `@id:38d864b9` and the state machine in discovery.md.
  Alternatives considered: Allowing stub creation for completed features — rejected per spec.

  ### Build Changes (needs PO approval: yes)
  - New runtime dependency: `libcst>=1.0.0` — reason: read/write Python test files preserving formatting and comments (Q19 in discovery.md).

  Rule: New stub generation
    As a developer
    I want a test stub to be created for each new Example in backlog and in-progress features
    So that I have a failing test ready to implement for every acceptance criterion

    @id:692972dd
    Example: New stub is created with the correct function name
      Given a backlog feature folder containing a .feature file with a new @id-tagged Example
      When pytest is invoked
      Then a test function named test_<feature_slug>_<id_hex> exists in the corresponding test file

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

    @id:e2b093d1
    Example: New stub for a Rule block is a method inside the rule class
      Given a backlog feature file with a Rule block containing a new @id-tagged Example
      When pytest is invoked
      Then the generated stub is a method inside class Test<RuleSlug> in <rule_slug>_test.py

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
