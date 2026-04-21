"""Tests for stub updates — function renames rule."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from pytest_beehave.sync_engine import run_sync as sync_stubs


class TestFunctionRenames:
    """Tests for the Function renames Rule."""

    def test_function_renames_b6b9ab28(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: an existing test stub whose function name does not match the current feature slug
        When: pytest is invoked
        Then: the test function is renamed to match test_<current_feature_slug>_<id_hex>
        """
        features_dir = tmp_path / "features"
        tests_dir = tmp_path / "tests"
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
        make_test_file(
            tests_dir,
            "new_feature",
            "examples",
            '''\
"""Tests for examples story."""

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
        sync_stubs(features_dir, tests_dir)
        test_file = tests_dir / "new_feature" / "examples_test.py"
        content = test_file.read_text(encoding="utf-8")
        assert "def test_new_feature_aabbccdd() -> None:" in content
        assert "def test_old_feature_aabbccdd" not in content

    def test_function_renames_d89540f9(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: a completed feature with a test stub whose docstring differs from the .feature file
        When: pytest is invoked
        Then: the completed feature test stub docstring is unchanged
        """
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
    Given the NEW condition
    When the NEW action runs
    Then the NEW result appears
""",
        )
        original_content = '''\
"""Tests for done examples story."""

import pytest


def test_done_feature_aabbccdd() -> None:
    """
    Given: the OLD condition
    When: the OLD action runs
    Then: the OLD result appears
    """
    raise NotImplementedError
'''
        make_test_file(tests_dir, "done_feature", "examples", original_content)
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
            "examples",
            '''\
"""Tests for examples story."""

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
        sync_stubs(features_dir, tests_dir)
        active_content = (tests_dir / "active_feature" / "examples_test.py").read_text(
            encoding="utf-8"
        )
        assert "Given: the active condition" in active_content
        done_content = (tests_dir / "done_feature" / "examples_test.py").read_text(
            encoding="utf-8"
        )
        assert done_content == original_content
