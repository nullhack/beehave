"""Tests for stub creation — docstring generation rule."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from pytest_beehave.sync_engine import run_sync as sync_stubs


class TestDocstringGeneration:
    """Tests for the Docstring generation Rule."""

    def test_stub_creation_db596443(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature with an Example containing And and But steps
        When: pytest is invoked
        Then: each And step appears as "And: <text>" and each But step appears as "But: <text>" in the docstring
        """
        features_dir = tmp_path / "features"
        tests_dir = tmp_path / "tests"
        make_feature(
            features_dir,
            "backlog",
            "my-feature",
            "my-story.feature",
            """\
Feature: My feature
  @id:aabbccdd
  Example: Steps with And and But
    Given a base condition
    And an additional condition
    When something happens
    Then a result occurs
    But not this other thing
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert "And: an additional condition" in content
        assert "But: not this other thing" in content

    def test_stub_creation_17b01d7a(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature with an Example containing a step written with the * bullet
        When: pytest is invoked
        Then: that step appears as "*: <text>" in the generated test stub docstring
        """
        features_dir = tmp_path / "features"
        tests_dir = tmp_path / "tests"
        make_feature(
            features_dir,
            "backlog",
            "my-feature",
            "my-story.feature",
            """\
Feature: My feature
  @id:aabbccdd
  Example: Steps with asterisk
    Given a base condition
    * a bullet step
    When something happens
    Then a result occurs
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert "*: a bullet step" in content

    def test_stub_creation_c56883ce(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature with an Example where a step has an attached multi-line doc string block
        When: pytest is invoked
        Then: the generated test stub docstring includes the doc string content indented below the step line
        """
        features_dir = tmp_path / "features"
        tests_dir = tmp_path / "tests"
        make_feature(
            features_dir,
            "backlog",
            "my-feature",
            "my-story.feature",
            '''\
Feature: My feature
  @id:aabbccdd
  Example: Step with doc string
    Given a step with attached content
      """
      line one
      line two
      """
    When something happens
    Then a result occurs
''',
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert "line one" in content
        assert "line two" in content
        lines = content.splitlines()
        step_line_idx = next(
            (
                i
                for i, ln in enumerate(lines)
                if "Given: a step with attached content" in ln
            ),
            -1,
        )
        assert step_line_idx >= 0
        assert any(
            "line one" in lines[j] and lines[j].startswith("    ")
            for j in range(step_line_idx + 1, min(step_line_idx + 6, len(lines)))
        )

    def test_stub_creation_2fc458f8(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature with an Example where a step has an attached data table
        When: pytest is invoked
        Then: the generated test stub docstring includes the table rows indented below the step line
        """
        features_dir = tmp_path / "features"
        tests_dir = tmp_path / "tests"
        make_feature(
            features_dir,
            "backlog",
            "my-feature",
            "my-story.feature",
            """\
Feature: My feature
  @id:aabbccdd
  Example: Step with data table
    Given a step with a table
      | col1 | col2 |
      | a    | b    |
      | c    | d    |
    When something happens
    Then a result occurs
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert "| col1 | col2 |" in content
        assert "| a    | b    |" in content
        lines = content.splitlines()
        step_line_idx = next(
            (i for i, ln in enumerate(lines) if "Given: a step with a table" in ln),
            -1,
        )
        assert step_line_idx >= 0
        assert any(
            "| col1 |" in lines[j] and lines[j].startswith("    ")
            for j in range(step_line_idx + 1, min(step_line_idx + 6, len(lines)))
        )

    def test_stub_creation_7f91cf3a(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature with a feature-level Background and a Rule-level Background
        When: pytest is invoked
        Then: the generated test stub docstring contains two "Background:" sections in order before the scenario steps
        """
        features_dir = tmp_path / "features"
        tests_dir = tmp_path / "tests"
        make_feature(
            features_dir,
            "backlog",
            "my-feature",
            "my-story.feature",
            """\
Feature: My feature
  Background:
    Given the shop is open

  Rule: Premium customers
    Background:
      And the customer has a premium account

    @id:aabbccdd
    Example: Premium order
      When a premium order is placed
      Then a 20% discount is applied
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "premium_customers")
        assert content.count("Background:") == 2
        first_bg = content.find("Background:")
        second_bg = content.find("Background:", first_bg + 1)
        when_idx = content.find("When: a premium order is placed")
        assert first_bg >= 0
        assert second_bg > first_bg
        assert when_idx > second_bg

    def test_stub_creation_9a4e199a(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature containing a Scenario Outline with placeholder values and an Examples table
        When: pytest is invoked
        Then: the generated test stub docstring contains the raw template step text followed by the Examples table
        """
        features_dir = tmp_path / "features"
        tests_dir = tmp_path / "tests"
        make_feature(
            features_dir,
            "backlog",
            "my-feature",
            "my-story.feature",
            """\
Feature: My feature
  @id:aabbccdd
  Scenario Outline: Template scenario
    Given a <thing>
    When it <action>
    Then it <result>

    Examples:
      | thing | action | result |
      | ball  | rolls  | stops  |
      | cube  | slides | falls  |
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert "Given: a <thing>" in content
        assert "When: it <action>" in content
        assert "| thing | action | result |" in content
        assert "| ball  | rolls  | stops  |" in content


def test_stub_creation_e5c3b271(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature with a Background section and a Scenario with its own steps
    When: pytest is invoked and the stub is created
    Then: the generated test stub docstring contains a blank line between the last Background step and the first Scenario step
    """
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    make_feature(
        features_dir,
        "backlog",
        "my-feature",
        "my-story.feature",
        """\
Feature: My feature
  Background:
    Given the shop is open

  @id:aabbccdd
  Example: Something happens
    When a customer arrives
    Then they are served
""",
    )
    sync_stubs(features_dir, tests_dir)
    content = read_test_file(tests_dir, "my_feature", "examples")
    lines = content.splitlines()
    bg_step_idx = next(
        (i for i, ln in enumerate(lines) if "Given: the shop is open" in ln), -1
    )
    assert bg_step_idx >= 0
    assert lines[bg_step_idx + 1] == ""
    when_idx = next(
        (i for i, ln in enumerate(lines) if "When: a customer arrives" in ln), -1
    )
    assert when_idx == bg_step_idx + 2
