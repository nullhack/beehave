"""Tests for deprecation marker sync story."""

from __future__ import annotations

from pathlib import Path

import pytest

from pytest_beehave.syncer import sync_stubs


def _make_feature(
    features_dir: Path,
    stage: str,
    folder: str,
    filename: str,
    content: str,
) -> None:
    """Write a .feature file under features_dir/<stage>/<folder>/<filename>."""
    feature_dir = features_dir / stage / folder
    feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / filename).write_text(content, encoding="utf-8")


def _make_test_file(
    tests_dir: Path,
    feature_slug: str,
    story_slug: str,
    content: str,
) -> Path:
    """Write a test file under tests_dir/<feature_slug>/<story_slug>_test.py."""
    test_dir = tests_dir / feature_slug
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / f"{story_slug}_test.py"
    test_file.write_text(content, encoding="utf-8")
    return test_file


@pytest.mark.unit
def test_deprecation_sync_f9b636df(tmp_path: Path) -> None:
    """
    Given: a backlog feature with an Example tagged @deprecated whose test stub lacks @pytest.mark.deprecated
    When: pytest is invoked
    Then: the test stub has @pytest.mark.deprecated applied
    """
    # Given
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    _make_feature(
        features_dir,
        "backlog",
        "my-feature",
        "my-story.feature",
        """\
Feature: My feature
  @deprecated @id:aabbccdd
  Example: A deprecated example
    Given a thing
    When it runs
    Then it works
""",
    )
    test_file = _make_test_file(
        tests_dir,
        "my_feature",
        "my_story",
        """\
\"\"\"Tests for my story.\"\"\"

import pytest


def test_my_feature_aabbccdd() -> None:
    \"\"\"
    Given: a thing
    When: it runs
    Then: it works
    \"\"\"
    raise NotImplementedError
""",
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = test_file.read_text(encoding="utf-8")
    assert "@pytest.mark.deprecated" in content
    deprecated_idx = content.index("@pytest.mark.deprecated")
    def_idx = content.index("def test_my_feature_aabbccdd")
    assert deprecated_idx < def_idx


@pytest.mark.unit
def test_deprecation_sync_fc372f15(tmp_path: Path) -> None:
    """
    Given: a completed feature with an Example tagged @deprecated whose test stub lacks @pytest.mark.deprecated
    When: pytest is invoked
    Then: the test stub has @pytest.mark.deprecated applied
    """
    # Given
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    _make_feature(
        features_dir,
        "completed",
        "done-feature",
        "done-story.feature",
        """\
Feature: Done feature
  @deprecated @id:aabbccdd
  Example: A deprecated done example
    Given it was done
    When checked
    Then it passes
""",
    )
    test_file = _make_test_file(
        tests_dir,
        "done_feature",
        "done_story",
        """\
\"\"\"Tests for done story.\"\"\"

import pytest


def test_done_feature_aabbccdd() -> None:
    \"\"\"
    Given: it was done
    When: checked
    Then: it passes
    \"\"\"
    raise NotImplementedError
""",
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = test_file.read_text(encoding="utf-8")
    assert "@pytest.mark.deprecated" in content
    deprecated_idx = content.index("@pytest.mark.deprecated")
    def_idx = content.index("def test_done_feature_aabbccdd")
    assert deprecated_idx < def_idx


@pytest.mark.unit
def test_deprecation_sync_7fcee92a(tmp_path: Path) -> None:
    """
    Given: a feature with an Example that no longer has the @deprecated tag but whose test stub has @pytest.mark.deprecated
    When: pytest is invoked
    Then: @pytest.mark.deprecated is removed from that test stub
    """
    # Given
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    _make_feature(
        features_dir,
        "in-progress",
        "my-feature",
        "my-story.feature",
        """\
Feature: My feature
  @id:aabbccdd
  Example: A formerly deprecated example
    Given a thing
    When it runs
    Then it works
""",
    )
    test_file = _make_test_file(
        tests_dir,
        "my_feature",
        "my_story",
        """\
\"\"\"Tests for my story.\"\"\"

import pytest


@pytest.mark.deprecated
def test_my_feature_aabbccdd() -> None:
    \"\"\"
    Given: a thing
    When: it runs
    Then: it works
    \"\"\"
    raise NotImplementedError
""",
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    content = test_file.read_text(encoding="utf-8")
    assert "@pytest.mark.deprecated" not in content
    assert "def test_my_feature_aabbccdd() -> None:" in content
