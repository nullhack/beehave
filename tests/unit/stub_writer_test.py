"""Unit tests for pytest_beehave.stub_writer module."""

from pathlib import Path

import pytest

from pytest_beehave.feature_parser import (
    ParsedExample,
    ParsedFeature,
    ParsedRule,
    ParsedStep,
)
from pytest_beehave.models import ExampleId, FeatureSlug, RuleSlug
from pytest_beehave.stub_writer import (
    StubSpec,
    SyncAction,
    _stub_function_source,
    mark_non_conforming,
    mark_orphan,
    toggle_deprecated_marker,
    write_stub_to_file,
)


def _make_example(hex_id: str, *, deprecated: bool = False) -> ParsedExample:
    return ParsedExample(
        example_id=ExampleId(hex_id),
        steps=(
            ParsedStep(
                keyword="Given", text="something", doc_string=None, data_table=None
            ),
        ),
        background_sections=(),
        outline_examples=None,
        is_deprecated=deprecated,
    )


def _make_feature(
    slug: str,
    rules: tuple[ParsedRule, ...] = (),
    top_level: tuple[ParsedExample, ...] = (),
) -> ParsedFeature:
    return ParsedFeature(
        path=Path(f"/fake/{slug}.feature"),
        feature_slug=FeatureSlug(slug),
        rules=rules,
        top_level_examples=top_level,
        is_deprecated=False,
    )


def test_sync_action_str_includes_detail_when_present() -> None:
    """
    Given: A SyncAction with a non-empty detail
    When: str() is called
    Then: Returns string including the detail in parens
    """
    action = SyncAction(
        action="ORPHAN", path=Path("/foo/bar_test.py"), detail="some detail"
    )
    result = str(action)
    assert "some detail" in result
    assert "ORPHAN" in result


def test_sync_action_str_excludes_detail_when_empty() -> None:
    """
    Given: A SyncAction with an empty detail
    When: str() is called
    Then: Returns string without parentheses
    """
    action = SyncAction(action="CREATE", path=Path("/foo/bar_test.py"))
    result = str(action)
    assert "(" not in result
    assert "CREATE" in result


def test_stub_function_source_deprecated_branch() -> None:
    """
    Given: A deprecated=True flag
    When: _stub_function_source is called
    Then: Returns source with @pytest.mark.deprecated decorator
    """
    source = _stub_function_source("test_my_feature_aabbccdd", "    Given: x", True)
    assert "@pytest.mark.deprecated" in source
    assert "@pytest.mark.skip" not in source


def test_write_stub_to_file_appends_to_existing_module_level(tmp_path: Path) -> None:
    """
    Given: An existing test file with one stub already
    When: write_stub_to_file is called for a new top-level example
    Then: The new stub is appended to the file
    """
    test_file = tmp_path / "examples_test.py"
    test_file.write_text(
        '"""Tests for examples story."""\n\nimport pytest\n\n\n'
        '@pytest.mark.skip(reason="not yet implemented")\n'
        "def test_my_feature_11111111() -> None:\n"
        '    """\n    Given: first\n    """\n'
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )
    example = _make_example("22222222")
    feature = _make_feature("my_feature", top_level=(example,))
    spec = StubSpec(
        feature_slug=FeatureSlug("my_feature"),
        rule_slug=None,
        example=example,
        feature=feature,
    )
    action = write_stub_to_file(test_file, spec)
    assert action.action == "UPDATE"
    content = test_file.read_text(encoding="utf-8")
    assert "test_my_feature_22222222" in content


def test_write_class_based_stub_raises_on_none_rule_slug(tmp_path: Path) -> None:
    """
    Given: A StubSpec with rule_slug=None passed to _write_class_based_stub
    When: write_stub_to_file tries to use it as a class-based stub
    Then: ValueError is raised
    """
    from pytest_beehave.stub_writer import _write_class_based_stub

    test_file = tmp_path / "rule_test.py"
    example = _make_example("aabbccdd")
    feature = _make_feature("my_feature", top_level=(example,))
    spec = StubSpec(
        feature_slug=FeatureSlug("my_feature"),
        rule_slug=None,
        example=example,
        feature=feature,
    )
    with pytest.raises(ValueError, match="rule_slug must not be None"):
        _write_class_based_stub(
            test_file,
            spec,
            "test_my_feature_aabbccdd",
            "def test_my_feature_aabbccdd() -> None:\n    pass\n",
        )


def test_write_class_based_stub_adds_to_existing_class(tmp_path: Path) -> None:
    """
    Given: A test file with an existing class
    When: write_stub_to_file is called for a new example in the same rule
    Then: The method is appended to the existing class
    """
    test_file = tmp_path / "my_rule_test.py"
    test_file.write_text(
        '"""Tests for my rule story."""\n\nimport pytest\n\n\n'
        "class TestMyRule:\n"
        '    @pytest.mark.skip(reason="not yet implemented")\n'
        "    def test_my_feature_11111111(self) -> None:\n"
        '        """\n        Given: first\n        """\n'
        "        raise NotImplementedError\n",
        encoding="utf-8",
    )
    example = _make_example("22222222")
    rule = ParsedRule(
        title="My Rule",
        rule_slug=RuleSlug("my_rule"),
        examples=(example,),
        is_deprecated=False,
    )
    feature = _make_feature("my_feature", rules=(rule,))
    spec = StubSpec(
        feature_slug=FeatureSlug("my_feature"),
        rule_slug=RuleSlug("my_rule"),
        example=example,
        feature=feature,
        stub_format="classes",
    )
    action = write_stub_to_file(test_file, spec)
    assert action.action == "UPDATE"
    content = test_file.read_text(encoding="utf-8")
    assert "test_my_feature_22222222" in content
    lines = content.splitlines()
    def_line = next((ln for ln in lines if "def test_my_feature_22222222" in ln), "")
    assert "(self)" in def_line


def test_write_class_based_stub_creates_new_class_in_existing_file(
    tmp_path: Path,
) -> None:
    """
    Given: A test file without the target class
    When: write_stub_to_file is called for a rule-based example
    Then: A new class block is added to the file
    """
    test_file = tmp_path / "other_rule_test.py"
    test_file.write_text(
        '"""Tests for other rule story."""\n\nimport pytest\n\n\n'
        "class TestOtherRule:\n"
        "    pass\n",
        encoding="utf-8",
    )
    example = _make_example("aabbccdd")
    rule = ParsedRule(
        title="New Rule",
        rule_slug=RuleSlug("new_rule"),
        examples=(example,),
        is_deprecated=False,
    )
    feature = _make_feature("my_feature", rules=(rule,))
    spec = StubSpec(
        feature_slug=FeatureSlug("my_feature"),
        rule_slug=RuleSlug("new_rule"),
        example=example,
        feature=feature,
        stub_format="classes",
    )
    action = write_stub_to_file(test_file, spec)
    assert action.action == "UPDATE"
    content = test_file.read_text(encoding="utf-8")
    assert "class TestNewRule:" in content
    assert "test_my_feature_aabbccdd" in content
    lines = content.splitlines()
    def_line = next((ln for ln in lines if "def test_my_feature_aabbccdd" in ln), "")
    assert "(self)" in def_line


def test_find_rule_returns_none_when_not_found() -> None:
    """
    Given: A feature with rules that don't match the target slug
    When: _find_rule is called with a non-existent slug
    Then: Returns None
    """
    from pytest_beehave.stub_writer import _find_rule

    rule = ParsedRule(
        title="Existing Rule",
        rule_slug=RuleSlug("existing_rule"),
        examples=(),
        is_deprecated=False,
    )
    feature = _make_feature("my_feature", rules=(rule,))
    result = _find_rule(feature, RuleSlug("non_existent"))
    assert result is None


def test_mark_orphan_returns_none_when_function_not_found(tmp_path: Path) -> None:
    """
    Given: A test file that doesn't contain the target function
    When: mark_orphan is called
    Then: Returns None
    """
    test_file = tmp_path / "examples_test.py"
    test_file.write_text(
        '"""Tests."""\n\nimport pytest\n\n\n'
        "def test_other_feature_aabbccdd() -> None:\n"
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )
    result = mark_orphan(test_file, "test_missing_feature_11111111")
    assert result is None


def test_mark_orphan_returns_none_when_already_marked(tmp_path: Path) -> None:
    """
    Given: A test file with a function already marked as orphan
    When: mark_orphan is called again
    Then: Returns None (no change)
    """
    test_file = tmp_path / "examples_test.py"
    test_file.write_text(
        '"""Tests."""\n\nimport pytest\n\n\n'
        '@pytest.mark.skip(reason="orphan: no matching @id in .feature files")\n'
        "def test_my_feature_aabbccdd() -> None:\n"
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )
    result = mark_orphan(test_file, "test_my_feature_aabbccdd")
    assert result is None


def test_mark_non_conforming_adds_marker(tmp_path: Path) -> None:
    """
    Given: A test file with a non-conforming function
    When: mark_non_conforming is called
    Then: A skip marker is prepended to the function
    """
    test_file = tmp_path / "wrong_test.py"
    correct = tmp_path / "correct" / "right_test.py"
    test_file.write_text(
        '"""Tests."""\n\nimport pytest\n\n\n'
        "def test_my_feature_aabbccdd() -> None:\n"
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )
    result = mark_non_conforming(
        test_file, "test_my_feature_aabbccdd", correct, "TestMyRule"
    )
    assert result is not None
    assert result.action == "NON_CONFORMING"
    content = test_file.read_text(encoding="utf-8")
    assert "non-conforming" in content
    assert "TestMyRule" in content


def test_mark_non_conforming_returns_none_when_function_not_found(
    tmp_path: Path,
) -> None:
    """
    Given: A test file without the target function
    When: mark_non_conforming is called
    Then: Returns None
    """
    test_file = tmp_path / "wrong_test.py"
    correct = tmp_path / "correct" / "right_test.py"
    test_file.write_text(
        '"""Tests."""\n\nimport pytest\n\n',
        encoding="utf-8",
    )
    result = mark_non_conforming(test_file, "test_missing_aabbccdd", correct, None)
    assert result is None


def test_mark_non_conforming_returns_none_when_already_marked(tmp_path: Path) -> None:
    """
    Given: A test file where the function already has a non-conforming marker
    When: mark_non_conforming is called again
    Then: Returns None (idempotent)
    """
    test_file = tmp_path / "wrong_test.py"
    correct = tmp_path / "correct" / "right_test.py"
    detail = f"should be in {correct}"
    test_file.write_text(
        '"""Tests."""\n\nimport pytest\n\n\n'
        f'@pytest.mark.skip(reason="non-conforming: {detail}")\n'
        "def test_my_feature_aabbccdd() -> None:\n"
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )
    result = mark_non_conforming(test_file, "test_my_feature_aabbccdd", correct, None)
    assert result is None


def test_toggle_deprecated_marker_skips_non_matching_functions(tmp_path: Path) -> None:
    """
    Given: A test file with multiple functions and only one matching the target
    When: toggle_deprecated_marker is called on the target function
    Then: Only the target function is affected; non-matching functions are skipped
    """
    test_file = tmp_path / "examples_test.py"
    test_file.write_text(
        '"""Tests."""\n\nimport pytest\n\n\n'
        "def test_my_feature_11111111() -> None:\n"
        "    raise NotImplementedError\n\n\n"
        "def test_my_feature_aabbccdd() -> None:\n"
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )
    result = toggle_deprecated_marker(
        test_file, "test_my_feature_aabbccdd", should_be_deprecated=True
    )
    assert result is not None
    assert result.action == "DEPRECATED"
    content = test_file.read_text(encoding="utf-8")
    # Only aabbccdd got the marker; 11111111 was skipped
    assert content.count("@pytest.mark.deprecated") == 1
    assert "def test_my_feature_aabbccdd" in content


def test_toggle_deprecated_marker_removes_when_not_deprecated(tmp_path: Path) -> None:
    """
    Given: A test file with @pytest.mark.deprecated on a function
    When: toggle_deprecated_marker is called with should_be_deprecated=False
    Then: The deprecated marker is removed
    """
    test_file = tmp_path / "examples_test.py"
    test_file.write_text(
        '"""Tests."""\n\nimport pytest\n\n\n'
        "@pytest.mark.deprecated\n"
        "def test_my_feature_aabbccdd() -> None:\n"
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )
    result = toggle_deprecated_marker(
        test_file, "test_my_feature_aabbccdd", should_be_deprecated=False
    )
    assert result is not None
    assert result.action == "DEPRECATED"
    content = test_file.read_text(encoding="utf-8")
    assert "@pytest.mark.deprecated" not in content


def test_write_class_based_stub_creates_new_file(tmp_path: Path) -> None:
    """
    Given: A non-existent test file and stub_format="classes"
    When: write_stub_to_file is called for a rule-based example
    Then: A new file is created with a class containing the method stub
    """
    test_file = tmp_path / "my_rule_test.py"
    example = _make_example("aabbccdd")
    rule = ParsedRule(
        title="My Rule",
        rule_slug=RuleSlug("my_rule"),
        examples=(example,),
        is_deprecated=False,
    )
    feature = _make_feature("my_feature", rules=(rule,))
    spec = StubSpec(
        feature_slug=FeatureSlug("my_feature"),
        rule_slug=RuleSlug("my_rule"),
        example=example,
        feature=feature,
        stub_format="classes",
    )
    action = write_stub_to_file(test_file, spec)
    assert action.action == "CREATE"
    content = test_file.read_text(encoding="utf-8")
    assert "class TestMyRule:" in content
    assert "test_my_feature_aabbccdd" in content
    lines = content.splitlines()
    def_line = next((ln for ln in lines if "def test_my_feature_aabbccdd" in ln), "")
    assert "(self)" in def_line


def test_stub_creation_scenario_outline_empty_examples_table_falls_back_to_skip(
    tmp_path: Path,
) -> None:
    """Scenario Outline with fewer than 2 rows in Examples falls back to skip marker."""
    test_file = tmp_path / "my_rule_test.py"
    example = ParsedExample(
        example_id=ExampleId("ccddee00"),
        steps=(
            ParsedStep(
                keyword="Given", text="x is <val>", doc_string=None, data_table=None
            ),
        ),
        background_sections=(),
        outline_examples="| val |\n",
        is_deprecated=False,
    )
    rule = ParsedRule(
        title="My Rule",
        rule_slug=RuleSlug("my_rule"),
        examples=(example,),
        is_deprecated=False,
    )
    feature = _make_feature("my_feature", rules=(rule,))
    spec = StubSpec(
        feature_slug=FeatureSlug("my_feature"),
        rule_slug=RuleSlug("my_rule"),
        example=example,
        feature=feature,
        stub_format="functions",
    )
    write_stub_to_file(test_file, spec)
    content = test_file.read_text(encoding="utf-8")
    assert '@pytest.mark.skip(reason="not yet implemented")' in content
