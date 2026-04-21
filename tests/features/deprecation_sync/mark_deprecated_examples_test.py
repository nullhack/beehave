"""Tests for deprecation sync — mark deprecated examples rule."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from pytest_beehave.sync_engine import run_sync as sync_stubs


class TestMarkDeprecatedExamples:
    """Tests for the Mark deprecated Examples Rule."""

    def test_deprecation_sync_f9b636df(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: a backlog feature with an Example tagged @deprecated whose test stub lacks @pytest.mark.deprecated
        When: pytest is invoked
        Then: the test stub has @pytest.mark.deprecated applied
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
  @deprecated @id:aabbccdd
  Example: A deprecated example
    Given a thing
    When it runs
    Then it works
""",
        )
        test_file = make_test_file(
            tests_dir,
            "my_feature",
            "examples",
            """\
\"\"\"Tests for my feature examples.\"\"\"

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
        sync_stubs(features_dir, tests_dir)
        content = test_file.read_text(encoding="utf-8")
        assert "@pytest.mark.deprecated" in content
        deprecated_idx = content.index("@pytest.mark.deprecated")
        def_idx = content.index("def test_my_feature_aabbccdd")
        assert deprecated_idx < def_idx

    def test_deprecation_sync_fc372f15(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: a completed feature with an Example tagged @deprecated whose test stub lacks @pytest.mark.deprecated
        When: pytest is invoked
        Then: the test stub has @pytest.mark.deprecated applied
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
  @deprecated @id:aabbccdd
  Example: A deprecated done example
    Given it was done
    When checked
    Then it passes
""",
        )
        test_file = make_test_file(
            tests_dir,
            "done_feature",
            "examples",
            """\
\"\"\"Tests for done feature examples.\"\"\"

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
        sync_stubs(features_dir, tests_dir)
        content = test_file.read_text(encoding="utf-8")
        assert "@pytest.mark.deprecated" in content
        deprecated_idx = content.index("@pytest.mark.deprecated")
        def_idx = content.index("def test_done_feature_aabbccdd")
        assert deprecated_idx < def_idx
