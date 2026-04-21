"""Tests for explicit functions format story."""

from pathlib import Path

from pytest_beehave.sync_engine import run_sync


def test_stub_format_config_f1e2d3c4(tmp_path: Path) -> None:
    """
    Given: a pyproject.toml with stub_format = "functions" under [tool.beehave]
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
    run_sync(features_dir, tests_dir, stub_format="functions")
    test_file = tests_dir / "my_feature" / "my_rule_test.py"
    content = test_file.read_text(encoding="utf-8")
    assert "def test_my_feature_aabbccdd() -> None:" in content
    assert "class " not in content
