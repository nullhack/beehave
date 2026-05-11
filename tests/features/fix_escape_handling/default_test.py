"""Test stubs for fix_escape_handling feature.

Generated from: docs/features/fix_escape_handling.feature
Rule: Escaped quotes in decorator text match unescaped quotes in feature step text
Rule: Genuine text differences are still detected
"""

from beehave.cli import _align_steps


def _setup_files(
    tmp_path, feature_content: str, test_content: str, name: str = "test_escape"
):
    """Create temp feature and test files, return (feature_path, test_dir)."""
    feature_file = tmp_path / "docs" / "features" / f"{name}.feature"
    feature_file.parent.mkdir(parents=True, exist_ok=True)
    feature_file.write_text(feature_content)

    test_file = tmp_path / "tests" / "features" / name / "default_test.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(test_content)

    return str(feature_file), str(test_file.parent)


def test_fix_escape_handling_d4e5f6a7(tmp_path) -> None:
    """Single-quoted escape matches unescaped apostrophe.

    Given a decorator with text "the hive's honey stores" and a feature step "the hive's honey stores"
    When fix() compares the texts
    Then no mismatch is reported
    """
    feature_content = (
        "Feature: Escape Test\n"
        "  Rule: Test\n"
        "    @id:d4e5f6a7\n"
        "    Example: Test\n"
        "      Given the hive's honey stores\n"
    )
    # File contains: @Given('the hive\'s honey stores')
    test_content = (
        "@Given('the hive\\'s honey stores')\ndef test_escape_d4e5f6a7():\n    pass\n"
    )
    feature_path, test_dir = _setup_files(tmp_path, feature_content, test_content)

    mismatches, _additions = _align_steps(feature_path, test_dir)

    assert len(mismatches) == 0


def test_fix_escape_handling_b8c9d0e1(tmp_path) -> None:
    """Double-quoted escape matches unescaped double quote.

    Given a decorator with text 'hive "Alpha" has 10 frames' and a feature step 'hive "Alpha" has 10 frames'
    When fix() compares the texts
    Then no mismatch is reported
    """
    feature_content = (
        "Feature: Escape Test\n"
        "  Rule: Test\n"
        "    @id:b8c9d0e1\n"
        "    Example: Test\n"
        '      Given hive "Alpha" has 10 frames\n'
    )
    # File contains: @Given("hive \"Alpha\" has 10 frames")
    test_content = (
        '@Given("hive \\"Alpha\\" has 10 frames")\n'
        "def test_escape_b8c9d0e1():\n"
        "    pass\n"
    )
    feature_path, test_dir = _setup_files(tmp_path, feature_content, test_content)

    mismatches, _additions = _align_steps(feature_path, test_dir)

    assert len(mismatches) == 0


def test_fix_escape_handling_f2a3b4c5(tmp_path) -> None:
    """Different step text is reported as mismatch.

    Given a decorator with text "the hive has 10 frames" and a feature step "the hive has 20 frames"
    When fix() compares the texts
    Then a mismatch is reported
    """
    feature_content = (
        "Feature: Escape Test\n"
        "  Rule: Test\n"
        "    @id:f2a3b4c5\n"
        "    Example: Test\n"
        "      Given the hive has 20 frames\n"
    )
    test_content = (
        "@Given('the hive has 10 frames')\ndef test_mismatch_f2a3b4c5():\n    pass\n"
    )
    feature_path, test_dir = _setup_files(tmp_path, feature_content, test_content)

    mismatches, _additions = _align_steps(feature_path, test_dir)

    assert len(mismatches) >= 1
    assert any(m["old_text"] == "the hive has 10 frames" for m in mismatches)


def test_fix_escape_handling_6d7e8f9a(tmp_path) -> None:
    """Escaped text that differs in content is reported as mismatch.

    Given a decorator with text "the hive's honey" and a feature step "the hive's nectar"
    When fix() compares the texts
    Then a mismatch is reported (content differs, not just escaping)
    """
    feature_content = (
        "Feature: Escape Test\n"
        "  Rule: Test\n"
        "    @id:6d7e8f9a\n"
        "    Example: Test\n"
        "      Given the hive's nectar\n"
    )
    # File contains: @Given('the hive\'s honey') — same escaping but different word
    test_content = (
        "@Given('the hive\\'s honey')\ndef test_escape_mismatch_6d7e8f9a():\n    pass\n"
    )
    feature_path, test_dir = _setup_files(tmp_path, feature_content, test_content)

    mismatches, _additions = _align_steps(feature_path, test_dir)

    assert len(mismatches) >= 1
