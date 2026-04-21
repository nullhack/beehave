"""Tests for no-rule feature unaffected story."""

from pathlib import Path

from pytest_beehave.sync_engine import run_sync


def test_stub_format_config_a7b8c9d0(tmp_path: Path) -> None:
    """
    Given: a pyproject.toml with stub_format = "classes" under [tool.beehave]
    And: a feature file with no Rule blocks
    When: pytest generates stubs for that feature
    Then: the stubs are module-level functions in examples_test.py with no class wrapper
    """
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    feature_dir = features_dir / "in-progress" / "my-feature"
    feature_dir.mkdir(parents=True)
    (feature_dir / "my-feature.feature").write_text(
        "Feature: My feature\n\n"
        "  @id:aabbccdd\n"
        "  Example: Something\n"
        "    Given a thing\n"
        "    When it runs\n"
        "    Then it works\n",
        encoding="utf-8",
    )
    run_sync(features_dir, tests_dir, stub_format="classes")
    test_file = tests_dir / "my_feature" / "examples_test.py"
    content = test_file.read_text(encoding="utf-8")
    assert "def test_my_feature_aabbccdd() -> None:" in content
    assert "class " not in content
