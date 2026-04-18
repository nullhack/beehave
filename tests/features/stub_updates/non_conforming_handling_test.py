"""Tests for stub updates — non-conforming handling rule."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from pytest_beehave.sync_engine import run_sync as sync_stubs


class TestNonConformingHandling:
    """Tests for the Non-conforming handling Rule."""

    @pytest.mark.unit
    def test_non_conforming_handling_4a7c2e81(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: a test function whose @id matches a current Example but is in the wrong file or class
        When: pytest is invoked
        Then: stub-sync creates a conforming stub in the correct location and marks the original with @pytest.mark.skip(reason="non-conforming: moved to <file>::<Class>")
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
  Rule: My rule
    @id:aabbccdd
    Example: A real example
      Given something
      When it runs
      Then it works
""",
        )
        # Put the test in the wrong file (not my_rule_test.py)
        wrong_file = make_test_file(
            tests_dir,
            "my_feature",
            "wrong_story",
            '''\
"""Tests for wrong story."""

import pytest


def test_my_feature_aabbccdd() -> None:
    """
    Given: something
    When: it runs
    Then: it works
    """
    raise NotImplementedError
''',
        )
        sync_stubs(features_dir, tests_dir)
        # Conforming stub created in correct location (rule slug uses underscores)
        correct_file = tests_dir / "my_feature" / "my_rule_test.py"
        assert correct_file.exists()
        correct_content = correct_file.read_text(encoding="utf-8")
        assert "def test_my_feature_aabbccdd" in correct_content
        # Original marked as non-conforming
        wrong_content = wrong_file.read_text(encoding="utf-8")
        assert "non-conforming" in wrong_content

    @pytest.mark.unit
    def test_non_conforming_handling_3f9d1b56(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: a non-conforming test already marked and a conforming stub already present in the correct location
        When: pytest is invoked
        Then: the non-conforming marker remains on the original test and the conforming stub is unchanged
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
  Rule: My rule
    @id:aabbccdd
    Example: A real example
      Given something
      When it runs
      Then it works
""",
        )
        # Conforming stub already in correct file (rule slug uses underscores → my_rule_test.py)
        conforming_content = '''\
"""Tests for my_rule story."""

import pytest


class TestMyRule:
    @pytest.mark.skip(reason="not yet implemented")
    def test_my_feature_aabbccdd(self) -> None:
        """
        Given: something
        When: it runs
        Then: it works
        """
        raise NotImplementedError
'''
        make_test_file(
            tests_dir,
            "my_feature",
            "my_rule",
            conforming_content,
        )
        # Original already marked non-conforming
        wrong_file = make_test_file(
            tests_dir,
            "my_feature",
            "wrong_story",
            '''\
"""Tests for wrong story."""

import pytest


@pytest.mark.skip(reason="non-conforming: should be in my_rule_test.py class TestMyRule")
def test_my_feature_aabbccdd() -> None:
    """
    Given: something
    When: it runs
    Then: it works
    """
    raise NotImplementedError
''',
        )
        sync_stubs(features_dir, tests_dir)
        wrong_content = wrong_file.read_text(encoding="utf-8")
        # Non-conforming marker still present
        assert "non-conforming" in wrong_content
        # Conforming stub is byte-for-byte unchanged
        correct_file = tests_dir / "my_feature" / "my_rule_test.py"
        correct_content = correct_file.read_text(encoding="utf-8")
        assert correct_content == conforming_content
