"""Tests for stub creation story."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from pytest_beehave.syncer import sync_stubs


@pytest.mark.unit
def test_stub_sync_692972dd(
    tmp_path: Path,
    make_feature: Callable[..., None],
) -> None:
    """
    Given: a backlog feature folder containing a .feature file with a new @id-tagged Example
    When: pytest is invoked
    Then: a test function named test_<feature_slug>_<id_hex> exists in the corresponding test file
    """
    # Given
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    test_file = tests_dir / "my_feature" / "my_story_test.py"
    assert test_file.exists()
    content = test_file.read_text(encoding="utf-8")
    assert "def test_my_feature_aabbccdd() -> None:" in content


@pytest.mark.unit
def test_stub_sync_d14d975f(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature folder containing a .feature file with a new @id-tagged Example
    When: pytest is invoked
    Then: the generated test function has no @pytest.mark decorator
    """
    # Given
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = read_test_file(tests_dir, "my_feature", "my_story")
    assert "def test_my_feature_aabbccdd() -> None:" in content
    # All lines before the def must not contain a @pytest.mark decorator
    func_idx = content.index("def test_my_feature_aabbccdd")
    block_before_def = content[:func_idx]
    lines_before = [ln for ln in block_before_def.splitlines() if ln.strip()]
    assert not any(line.startswith("@pytest.mark") for line in lines_before)


@pytest.mark.unit
def test_stub_sync_db596443(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature with an Example containing And and But steps
    When: pytest is invoked
    Then: each And step appears as "And: <text>" and each But step appears as "But: <text>" in the docstring
    """
    # Given
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
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = read_test_file(tests_dir, "my_feature", "my_story")
    assert "And: an additional condition" in content
    assert "But: not this other thing" in content


@pytest.mark.unit
def test_stub_sync_17b01d7a(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature with an Example containing a step written with the * bullet
    When: pytest is invoked
    Then: that step appears as "*: <text>" in the generated test stub docstring
    """
    # Given
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
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = read_test_file(tests_dir, "my_feature", "my_story")
    assert "*: a bullet step" in content


@pytest.mark.unit
def test_stub_sync_c56883ce(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature with an Example where a step has an attached multi-line doc string block
    When: pytest is invoked
    Then: the generated test stub docstring includes the doc string content indented below the step line
    """
    # Given
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
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = read_test_file(tests_dir, "my_feature", "my_story")
    assert "line one" in content
    assert "line two" in content
    # The doc string content must appear indented below the step line
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


@pytest.mark.unit
def test_stub_sync_2fc458f8(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature with an Example where a step has an attached data table
    When: pytest is invoked
    Then: the generated test stub docstring includes the table rows indented below the step line
    """
    # Given
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
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = read_test_file(tests_dir, "my_feature", "my_story")
    assert "| col1 | col2 |" in content
    assert "| a    | b    |" in content
    # Table rows must appear indented below the step line
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


@pytest.mark.unit
def test_stub_sync_7f91cf3a(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature with a feature-level Background and a Rule-level Background
    When: pytest is invoked
    Then: the generated test stub docstring contains two "Background:" sections in order before the scenario steps
    """
    # Given
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
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = read_test_file(tests_dir, "my_feature", "my_story")
    assert content.count("Background:") == 2
    first_bg = content.find("Background:")
    second_bg = content.find("Background:", first_bg + 1)
    when_idx = content.find("When: a premium order is placed")
    assert first_bg >= 0
    assert second_bg > first_bg
    assert when_idx > second_bg


@pytest.mark.unit
def test_stub_sync_9a4e199a(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature containing a Scenario Outline with placeholder values and an Examples table
    When: pytest is invoked
    Then: the generated test stub docstring contains the raw template step text followed by the Examples table
    """
    # Given
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
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = read_test_file(tests_dir, "my_feature", "my_story")
    assert "Given: a <thing>" in content
    assert "When: it <action>" in content
    assert "| thing | action | result |" in content
    assert "| ball  | rolls  | stops  |" in content


@pytest.mark.unit
def test_stub_sync_777a9638(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature folder containing a .feature file with a new @id-tagged Example
    When: pytest is invoked
    Then: the generated test function body ends with raise NotImplementedError
    """
    # Given
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = read_test_file(tests_dir, "my_feature", "my_story")
    assert "raise NotImplementedError" in content
    non_empty_lines = [ln for ln in content.splitlines() if ln.strip()]
    assert non_empty_lines[-1].strip() == "raise NotImplementedError"


@pytest.mark.unit
def test_stub_sync_38d864b9(
    tmp_path: Path,
    make_feature: Callable[..., None],
) -> None:
    """
    Given: a completed feature folder containing a .feature file with a new @id-tagged Example
    When: pytest is invoked
    Then: no new test stub is created for that Example
    """
    # Given
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    make_feature(
        features_dir,
        "completed",
        "done-feature",
        "done-story.feature",
        """\
Feature: Done feature
  @id:aabbccdd
  Example: Something was done
    Given it was done
    When checked
    Then it passes
""",
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    test_file = tests_dir / "done_feature" / "done_story_test.py"
    assert not test_file.exists()


@pytest.mark.unit
def test_stub_sync_bba184c0(
    tmp_path: Path,
    make_feature: Callable[..., None],
    read_test_file: Callable[..., str],
) -> None:
    """
    Given: a backlog feature folder containing a .feature file with a new @id-tagged Example
    When: pytest is invoked
    Then: the generated test function body contains no "# Given", "# When", or "# Then" comment lines
    """
    # Given
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = read_test_file(tests_dir, "my_feature", "my_story")
    assert "def test_my_feature_aabbccdd() -> None:" in content
    # Extract the function body (after the closing triple-quote of the docstring)
    func_start = content.index("def test_my_feature_aabbccdd")
    first_docstring_open = content.index('"""', func_start)
    docstring_close = content.index('"""', first_docstring_open + 3) + 3
    body = content[docstring_close:]
    assert "# Given" not in body
    assert "# When" not in body
    assert "# Then" not in body


@pytest.mark.unit
def test_stub_sync_edc964fc(
    tmp_path: Path,
    make_feature: Callable[..., None],
) -> None:
    """
    Given: a backlog feature folder whose name contains hyphens (e.g. "my-feature")
    When: pytest is invoked
    Then: the test file is created at tests/features/my_feature/ not tests/features/my-feature/
    """
    # Given
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    assert (tests_dir / "my_feature" / "my_story_test.py").exists()
    assert not (tests_dir / "my-feature").exists()
