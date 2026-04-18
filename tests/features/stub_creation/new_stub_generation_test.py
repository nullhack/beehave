"""Tests for stub creation — new stub generation rule."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from pytest_beehave.sync_engine import run_sync as sync_stubs


class TestNewStubGeneration:
    """Tests for the New stub generation Rule."""

    def test_stub_creation_692972dd(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
    ) -> None:
        """
        Given: a backlog feature folder containing a .feature file with a new @id-tagged Example
        When: pytest is invoked
        Then: a test function named test_<feature_slug>_<id_hex> exists in the corresponding test file
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
        )
        sync_stubs(features_dir, tests_dir)
        test_file = tests_dir / "my_feature" / "examples_test.py"
        assert test_file.exists()
        content = test_file.read_text(encoding="utf-8")
        assert "def test_my_feature_aabbccdd() -> None:" in content

    @pytest.mark.deprecated
    def test_stub_creation_d14d975f(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature folder containing a .feature file with a new @id-tagged Example
        When: pytest is invoked
        Then: the generated test function has no @pytest.mark decorator
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert "def test_my_feature_aabbccdd() -> None:" in content
        func_idx = content.index("def test_my_feature_aabbccdd")
        block_before_def = content[:func_idx]
        lines_before = [ln for ln in block_before_def.splitlines() if ln.strip()]
        assert not any(line.startswith("@pytest.mark") for line in lines_before)

    def test_stub_creation_a4c781f2(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature folder containing a .feature file with a new @id-tagged Example
        When: pytest is invoked
        Then: the generated test function has @pytest.mark.skip(reason="not yet implemented") applied
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert '@pytest.mark.skip(reason="not yet implemented")' in content
        skip_idx = content.index("@pytest.mark.skip")
        def_idx = content.index("def test_my_feature_aabbccdd")
        assert skip_idx < def_idx

    def test_stub_creation_e2b093d1(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature file with a Rule block containing a new @id-tagged Example
        When: pytest is invoked
        Then: the generated stub is a method inside class Test<RuleSlug> in <rule-slug>_test.py
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
  Rule: Premium customers
    @id:aabbccdd
    Example: Premium order
      Given a premium customer
      When an order is placed
      Then a discount is applied
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "premium_customers")
        assert "class TestPremiumCustomers:" in content
        assert "def test_my_feature_aabbccdd" in content
        lines = content.splitlines()
        def_line = next(
            (ln for ln in lines if "def test_my_feature_aabbccdd" in ln), ""
        )
        assert def_line.startswith("    ")

    def test_stub_creation_f1a5c823(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature file with no Rule blocks containing a new @id-tagged Example
        When: pytest is invoked
        Then: the generated stub is a module-level function in examples_test.py
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert "def test_my_feature_aabbccdd() -> None:" in content
        lines = content.splitlines()
        def_line = next(
            (ln for ln in lines if "def test_my_feature_aabbccdd" in ln), ""
        )
        assert def_line.startswith("def ")

    def test_stub_creation_777a9638(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature folder containing a .feature file with a new @id-tagged Example
        When: pytest is invoked
        Then: the generated test function body ends with raise NotImplementedError
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert "raise NotImplementedError" in content
        non_empty_lines = [ln for ln in content.splitlines() if ln.strip()]
        assert non_empty_lines[-1].strip() == "raise NotImplementedError"

    def test_stub_creation_bba184c0(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
        read_test_file: Callable[..., str],
    ) -> None:
        """
        Given: a backlog feature folder containing a .feature file with a new @id-tagged Example
        When: pytest is invoked
        Then: the generated test function body contains no "# Given", "# When", or "# Then" comment lines
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
        )
        sync_stubs(features_dir, tests_dir)
        content = read_test_file(tests_dir, "my_feature", "examples")
        assert "def test_my_feature_aabbccdd() -> None:" in content
        func_start = content.index("def test_my_feature_aabbccdd")
        first_docstring_open = content.index('"""', func_start)
        docstring_close = content.index('"""', first_docstring_open + 3) + 3
        body = content[docstring_close:]
        assert "# Given" not in body
        assert "# When" not in body
        assert "# Then" not in body

    def test_stub_creation_edc964fc(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
    ) -> None:
        """
        Given: a backlog feature folder whose name contains hyphens (e.g. "my-feature")
        When: pytest is invoked
        Then: the test file is created at tests/features/my_feature/ not tests/features/my-feature/
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
  Example: Something happens
    Given a thing
    When it runs
    Then it works
""",
        )
        sync_stubs(features_dir, tests_dir)
        assert (tests_dir / "my_feature" / "examples_test.py").exists()
        assert not (tests_dir / "my-feature").exists()

    def test_stub_creation_38d864b9(
        self,
        tmp_path: Path,
        make_feature: Callable[..., None],
    ) -> None:
        """
        Given: a completed feature folder containing a .feature file with a new @id-tagged Example
        When: pytest is invoked
        Then: no new test stub is created for that Example
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
    Given it was done
    When checked
    Then it passes
""",
        )
        sync_stubs(features_dir, tests_dir)
        # For a feature with no Rule blocks, the sync engine would create examples_test.py
        # For a completed feature, no new stubs are created at all
        test_file = tests_dir / "done_feature" / "examples_test.py"
        assert not test_file.exists()
