"""Tests for stub update story."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from pytest_beehave.syncer import sync_stubs


@pytest.mark.unit
def test_stub_sync_bdb8e233(
    tmp_path: Path,
    make_feature: Callable[..., None],
    make_test_file: Callable[..., Path],
) -> None:
    """
    Given: an existing test stub whose docstring does not match the current step text in the .feature file
    When: pytest is invoked
    Then: the test stub docstring matches the current step text from the .feature file
    """
    # Given
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    make_feature(
        features_dir,
        "in-progress",
        "my-feature",
        "my-story.feature",
        """\
Feature: My feature
  @id:aabbccdd
  Example: Updated scenario
    Given the new condition
    When the new action runs
    Then the new result appears
""",
    )
    # Existing stub has stale docstring
    make_test_file(
        tests_dir,
        "my_feature",
        "my_story",
        '''\
"""Tests for my story."""

import pytest


def test_my_feature_aabbccdd() -> None:
    """
    Given: the OLD condition
    When: the OLD action runs
    Then: the OLD result appears
    """
    raise NotImplementedError
''',
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    test_file = tests_dir / "my_feature" / "my_story_test.py"
    content = test_file.read_text(encoding="utf-8")
    assert "Given: the new condition" in content
    assert "When: the new action runs" in content
    assert "Then: the new result appears" in content
    assert "OLD" not in content


@pytest.mark.unit
def test_stub_sync_6bb59874(
    tmp_path: Path,
    make_feature: Callable[..., None],
    make_test_file: Callable[..., Path],
) -> None:
    """
    Given: an existing test stub with a custom implementation in the function body
    When: pytest is invoked and the .feature file step text has changed
    Then: the test function body below the docstring is unchanged
    """
    # Given
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    make_feature(
        features_dir,
        "in-progress",
        "my-feature",
        "my-story.feature",
        """\
Feature: My feature
  @id:aabbccdd
  Example: Updated scenario
    Given the new condition
    When the new action runs
    Then the new result appears
""",
    )
    custom_body = "    result = my_function()\n    assert result == 42\n"
    make_test_file(
        tests_dir,
        "my_feature",
        "my_story",
        f'''\
"""Tests for my story."""

import pytest


def test_my_feature_aabbccdd() -> None:
    """
    Given: the OLD condition
    When: the OLD action runs
    Then: the OLD result appears
    """
{custom_body}''',
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    test_file = tests_dir / "my_feature" / "my_story_test.py"
    content = test_file.read_text(encoding="utf-8")
    # The docstring must have been updated to the new step text
    assert "Given: the new condition" in content
    # The custom body must be preserved unchanged
    assert "result = my_function()" in content
    assert "assert result == 42" in content


@pytest.mark.unit
def test_stub_sync_b6b9ab28(
    tmp_path: Path,
    make_feature: Callable[..., None],
    make_test_file: Callable[..., Path],
) -> None:
    """
    Given: an existing test stub whose function name does not match the current feature slug
    When: pytest is invoked
    Then: the test function is renamed to match test_<current_feature_slug>_<id_hex>
    """
    # Given
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    # Feature folder is now "new-feature" (slug: new_feature)
    make_feature(
        features_dir,
        "in-progress",
        "new-feature",
        "my-story.feature",
        """\
Feature: New feature
  @id:aabbccdd
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
    )
    # Existing test file has old slug "old_feature" in function name
    make_test_file(
        tests_dir,
        "new_feature",
        "my_story",
        '''\
"""Tests for my story."""

import pytest


def test_old_feature_aabbccdd() -> None:
    """
    Given: a thing
    When: it runs
    Then: it works
    """
    raise NotImplementedError
''',
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then
    test_file = tests_dir / "new_feature" / "my_story_test.py"
    content = test_file.read_text(encoding="utf-8")
    assert "def test_new_feature_aabbccdd() -> None:" in content
    assert "def test_old_feature_aabbccdd" not in content


@pytest.mark.unit
def test_stub_sync_d89540f9(
    tmp_path: Path,
    make_feature: Callable[..., None],
    make_test_file: Callable[..., Path],
) -> None:
    """
    Given: a completed feature with a test stub whose docstring differs from the .feature file
    When: pytest is invoked
    Then: the completed feature test stub docstring is unchanged
    """
    # Given
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    # Completed feature: docstring differs from .feature file
    make_feature(
        features_dir,
        "completed",
        "done-feature",
        "done-story.feature",
        """\
Feature: Done feature
  @id:aabbccdd
  Example: Something was done
    Given the NEW condition
    When the NEW action runs
    Then the NEW result appears
""",
    )
    original_content = '''\
"""Tests for done story."""

import pytest


def test_done_feature_aabbccdd() -> None:
    """
    Given: the OLD condition
    When: the OLD action runs
    Then: the OLD result appears
    """
    raise NotImplementedError
'''
    make_test_file(tests_dir, "done_feature", "done_story", original_content)
    # In-progress feature — to confirm the sync mechanism works for active features
    make_feature(
        features_dir,
        "in-progress",
        "active-feature",
        "active-story.feature",
        """\
Feature: Active feature
  @id:11223344
  Example: Active scenario
    Given the active condition
    When the active action runs
    Then the active result appears
""",
    )
    make_test_file(
        tests_dir,
        "active_feature",
        "active_story",
        '''\
"""Tests for active story."""

import pytest


def test_active_feature_11223344() -> None:
    """
    Given: the STALE condition
    When: the STALE action runs
    Then: the STALE result appears
    """
    raise NotImplementedError
''',
    )
    # When
    sync_stubs(features_dir, tests_dir)
    # Then — in-progress stub was updated (proves sync works)
    active_content = (tests_dir / "active_feature" / "active_story_test.py").read_text(
        encoding="utf-8"
    )
    assert "Given: the active condition" in active_content
    # Completed stub was NOT updated
    done_content = (tests_dir / "done_feature" / "done_story_test.py").read_text(
        encoding="utf-8"
    )
    assert done_content == original_content
