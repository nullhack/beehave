"""Tests for deprecation sync — mark deprecated via tag inheritance rule."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from pytest_beehave.sync_engine import run_sync as sync_stubs


class TestMarkDeprecatedViaTagInheritance:
    """Tests for the Mark deprecated via tag inheritance Rule."""

    @pytest.mark.unit
    def test_deprecation_sync_b3d7f942(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: a backlog feature with a Rule tagged @deprecated containing multiple Examples
        When: pytest is invoked
        Then: all test stubs for Examples in that Rule have @pytest.mark.deprecated applied
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
  @deprecated
  Rule: Old rule
    @id:aabbccdd
    Example: First example
      Given something
      When it runs
      Then it works
    @id:11223344
    Example: Second example
      Given another thing
      When it runs
      Then it also works
""",
        )
        test_file = make_test_file(
            tests_dir,
            "my_feature",
            "old_rule",
            '''\
"""Tests for my feature old rule."""

import pytest


def test_my_feature_aabbccdd() -> None:
    """
    Given: something
    When: it runs
    Then: it works
    """
    raise NotImplementedError


def test_my_feature_11223344() -> None:
    """
    Given: another thing
    When: it runs
    Then: it also works
    """
    raise NotImplementedError
''',
        )
        sync_stubs(features_dir, tests_dir)
        content = test_file.read_text(encoding="utf-8")
        assert content.count("@pytest.mark.deprecated") == 2

    @pytest.mark.unit
    def test_deprecation_sync_a9e1c504(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: a backlog feature tagged @deprecated at the Feature level containing multiple Rules and Examples
        When: pytest is invoked
        Then: all test stubs for all Examples in that feature have @pytest.mark.deprecated applied
        """
        features_dir = tmp_path / "features"
        tests_dir = tmp_path / "tests"
        make_feature(
            features_dir,
            "backlog",
            "my-feature",
            "my-story.feature",
            """\
@deprecated
Feature: My feature
  Rule: Rule one
    @id:aabbccdd
    Example: First example
      Given something
      When it runs
      Then it works
  Rule: Rule two
    @id:11223344
    Example: Second example
      Given another thing
      When it runs
      Then it also works
""",
        )
        test_file_one = make_test_file(
            tests_dir,
            "my_feature",
            "rule_one",
            '''\
"""Tests for my feature rule one."""

import pytest


class TestRuleOne:
    def test_my_feature_aabbccdd(self) -> None:
        """
        Given: something
        When: it runs
        Then: it works
        """
        raise NotImplementedError
''',
        )
        test_file_two = make_test_file(
            tests_dir,
            "my_feature",
            "rule_two",
            '''\
"""Tests for my feature rule two."""

import pytest


class TestRuleTwo:
    def test_my_feature_11223344(self) -> None:
        """
        Given: another thing
        When: it runs
        Then: it also works
        """
        raise NotImplementedError
''',
        )
        sync_stubs(features_dir, tests_dir)
        content_one = test_file_one.read_text(encoding="utf-8")
        content_two = test_file_two.read_text(encoding="utf-8")
        assert "@pytest.mark.deprecated" in content_one
        assert "@pytest.mark.deprecated" in content_two

    @pytest.mark.unit
    def test_deprecation_sync_d6f8b231(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: a Rule whose @deprecated tag has been removed but whose child test stubs all have @pytest.mark.deprecated
        When: pytest is invoked
        Then: @pytest.mark.deprecated is removed from all child test stubs of that Rule
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
  Rule: Active rule
    @id:aabbccdd
    Example: First example
      Given something
      When it runs
      Then it works
    @id:11223344
    Example: Second example
      Given another thing
      When it runs
      Then it also works
""",
        )
        test_file = make_test_file(
            tests_dir,
            "my_feature",
            "active_rule",
            '''\
"""Tests for my feature active rule."""

import pytest


class TestActiveRule:
    @pytest.mark.deprecated
    def test_my_feature_aabbccdd(self) -> None:
        """
        Given: something
        When: it runs
        Then: it works
        """
        raise NotImplementedError

    @pytest.mark.deprecated
    def test_my_feature_11223344(self) -> None:
        """
        Given: another thing
        When: it runs
        Then: it also works
        """
        raise NotImplementedError
''',
        )
        sync_stubs(features_dir, tests_dir)
        content = test_file.read_text(encoding="utf-8")
        assert "@pytest.mark.deprecated" not in content
