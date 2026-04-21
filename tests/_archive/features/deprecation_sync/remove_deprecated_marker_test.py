"""Tests for deprecation sync — remove deprecated marker rule."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from pytest_beehave.sync_engine import run_sync as sync_stubs


class TestRemoveDeprecatedMarker:
    """Tests for the Remove deprecated marker Rule."""

    def test_deprecation_sync_7fcee92a(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        make_test_file: Callable[..., Path],
    ) -> None:
        """
        Given: a feature with an Example that no longer has the @deprecated tag but whose test stub has @pytest.mark.deprecated
        When: pytest is invoked
        Then: @pytest.mark.deprecated is removed from that test stub
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
  Example: A formerly deprecated example
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
        sync_stubs(features_dir, tests_dir)
        content = test_file.read_text(encoding="utf-8")
        assert "@pytest.mark.deprecated" not in content
        assert "def test_my_feature_aabbccdd() -> None:" in content
