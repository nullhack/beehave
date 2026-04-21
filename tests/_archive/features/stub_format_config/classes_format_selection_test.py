"""Tests for classes format selection story."""

from pathlib import Path

from pytest_beehave.sync_engine import run_sync


def test_stub_format_config_a2b3c4d5(tmp_path: Path) -> None:
    """
    Given: a pyproject.toml with stub_format = "classes" under [tool.beehave]
    When: pytest generates a stub for a Rule-block Example
    Then: the stub is a method inside class Test<RuleSlug> in <rule_slug>_test.py
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
    run_sync(features_dir, tests_dir, stub_format="classes")
    test_file = tests_dir / "my_feature" / "my_rule_test.py"
    content = test_file.read_text(encoding="utf-8")
    assert "class TestMyRule:" in content
    lines = content.splitlines()
    def_line = next((ln for ln in lines if "def test_my_feature_aabbccdd" in ln), "")
    assert def_line.startswith("    ")
    assert "(self)" in def_line


def test_stub_format_config_b3c4d5e6(tmp_path: Path) -> None:
    """
    Given: a pyproject.toml with stub_format = "classes" and a Rule titled "Wall bounce"
    When: pytest generates a stub for an Example under that Rule
    Then: the stub is inside a class named TestWallBounce
    """
    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests"
    feature_dir = features_dir / "in-progress" / "my-feature"
    feature_dir.mkdir(parents=True)
    (feature_dir / "my-feature.feature").write_text(
        "Feature: My feature\n\n"
        "  Rule: Wall bounce\n"
        "    @id:aabbccdd\n"
        "    Example: Something\n"
        "      Given a thing\n"
        "      When it runs\n"
        "      Then it works\n",
        encoding="utf-8",
    )
    run_sync(features_dir, tests_dir, stub_format="classes")
    test_file = tests_dir / "my_feature" / "wall_bounce_test.py"
    content = test_file.read_text(encoding="utf-8")
    assert "class TestWallBounce:" in content
