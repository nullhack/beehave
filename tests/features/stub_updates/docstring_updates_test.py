"""Tests for stub updates — docstring updates rule."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from pytest_beehave.sync_engine import run_sync as sync_stubs


class TestDocstringUpdates:
    """Tests for the Docstring updates Rule."""

    def test_docstring_updates_bdb8e233(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: an existing test stub whose docstring does not match the current step text in the .feature file
        When: pytest is invoked
        Then: the test stub docstring matches the current step text from the .feature file
        """
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
        make_test_file(
            tests_dir,
            "my_feature",
            "examples",
            '''\
"""Tests for examples story."""

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
        sync_stubs(features_dir, tests_dir)
        test_file = tests_dir / "my_feature" / "examples_test.py"
        content = test_file.read_text(encoding="utf-8")
        assert "Given: the new condition" in content
        assert "When: the new action runs" in content
        assert "Then: the new result appears" in content
        assert "OLD" not in content

    def test_docstring_updates_6bb59874(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: an existing test stub with a custom implementation in the function body
        When: pytest is invoked and the .feature file step text has changed
        Then: the test function body below the docstring is unchanged
        """
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
            "examples",
            f'''\
"""Tests for examples story."""

import pytest


def test_my_feature_aabbccdd() -> None:
    """
    Given: the OLD condition
    When: the OLD action runs
    Then: the OLD result appears
    """
{custom_body}''',
        )
        sync_stubs(features_dir, tests_dir)
        test_file = tests_dir / "my_feature" / "examples_test.py"
        content = test_file.read_text(encoding="utf-8")
        assert "Given: the new condition" in content
        assert "result = my_function()" in content
        assert "assert result == 42" in content


@pytest.mark.skip(reason="not yet implemented")
def test_stub_updates_d6a4f382() -> None:
    """
    Given: an existing test stub for a feature with a Background section whose docstring does not have a blank line between Background steps and Scenario steps
    When: pytest is invoked and the stub docstring is updated
    Then: the updated docstring contains a blank line between the last Background step and the first Scenario step
    """
    raise NotImplementedError
