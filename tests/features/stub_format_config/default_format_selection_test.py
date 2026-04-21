"""Tests for default format selection story."""

from pathlib import Path

import pytest

from pytest_beehave.sync_engine import run_sync


def test_stub_format_config_a1b2c3d4(tmp_path: Path) -> None:
    """
    Given: a pyproject.toml with no stub_format key under [tool.beehave]
    When: pytest generates a stub for a Rule-block Example
    Then: the stub is a top-level function def test_<feature_slug>_<@id> with no class wrapper
    """
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    feature_dir = features_dir / "in-progress" / "my-feature"
    feature_dir.mkdir(parents=True)
    (feature_dir / "my-feature.feature").write_text(
        "Feature: My feature\n\n"
        "  Rule: My rule\n"
        "    @id:aabbccdd\n"
        "    Example: Something\n"
        "      Given a thing\n"
        "      When it runs\n"
        "      Then it works\n",
        encoding="utf-8",
    )
    run_sync(features_dir, tests_dir)
    test_file = tests_dir / "my_feature" / "my_rule_test.py"
    assert test_file.exists()
    content = test_file.read_text(encoding="utf-8")
    assert "def test_my_feature_aabbccdd() -> None:" in content
    assert "class " not in content


@pytest.mark.slow
def test_stub_format_config_b2c3d4e5(tmp_path: Path) -> None:
    """
    Given: a pyproject.toml with no stub_format key under [tool.beehave]
    When: pytest starts up
    Then: pytest starts without any stub_format-related error
    """
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.beehave]\nfeatures_path = "docs/features"\n', encoding="utf-8"
    )
    features_dir = tmp_path / "docs" / "features" / "backlog"
    features_dir.mkdir(parents=True)
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    conftest = tmp_path / "conftest.py"
    conftest.write_text("", encoding="utf-8")

    result = pytest.main(["--no-cov", "--co", "-q", str(tmp_path)], plugins=[])
    assert result in (0, 5)  # 0=ok, 5=no tests collected — both mean no error
