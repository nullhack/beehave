"""Unit tests for pytest_beehave.feature_parser module."""

from pathlib import Path
from typing import Any

from pytest_beehave.feature_parser import (
    _extract_id_from_tags,
    _render_data_table,
    _render_examples_table,
    collect_all_example_ids,
    parse_feature,
)
from pytest_beehave.models import ExampleId, FeatureSlug


def test_render_data_table_empty_rows() -> None:
    """
    Given: An empty rows list
    When: _render_data_table is called
    Then: Returns empty string
    """
    result = _render_data_table([])
    assert result == ""


def test_render_examples_table_empty_examples() -> None:
    """
    Given: An empty examples list
    When: _render_examples_table is called
    Then: Returns empty string
    """
    result = _render_examples_table([])
    assert result == ""


def test_render_examples_table_no_rows() -> None:
    """
    Given: An examples list with no tableHeader and no tableBody
    When: _render_examples_table is called
    Then: Returns 'Examples:'
    """
    examples: list[dict[str, Any]] = [{"tableBody": []}]
    result = _render_examples_table(examples)
    assert result == "Examples:"


def test_extract_id_from_tags_returns_none_when_no_match() -> None:
    """
    Given: A list of tags with no @id tag
    When: _extract_id_from_tags is called
    Then: Returns None
    """
    tags = [{"name": "@slow"}, {"name": "@deprecated"}]
    result = _extract_id_from_tags(tags)
    assert result is None


def test_parse_feature_uses_parent_name_when_folder_name_is_none(
    tmp_path: Path,
) -> None:
    """
    Given: A .feature file at path/my-feature/story.feature
    When: parse_feature is called without folder_name
    Then: Uses the parent directory name as the folder_name
    """
    feature_dir = tmp_path / "my-feature"
    feature_dir.mkdir()
    feature_file = feature_dir / "story.feature"
    feature_file.write_text("Feature: My Feature\n", encoding="utf-8")

    result = parse_feature(feature_file)

    assert result.feature_slug == FeatureSlug.from_folder_name("my-feature")


def test_parse_feature_returns_empty_when_feature_node_missing(tmp_path: Path) -> None:
    """
    Given: A .feature file with no Feature: block
    When: parse_feature is called
    Then: Returns a ParsedFeature with empty rules and examples
    """
    feature_file = tmp_path / "empty.feature"
    feature_file.write_text("", encoding="utf-8")

    result = parse_feature(feature_file, folder_name="empty")

    assert result.rules == ()
    assert result.top_level_examples == ()
    assert result.is_deprecated is False


def test_parse_feature_skips_scenario_without_id_tag(tmp_path: Path) -> None:
    """
    Given: A .feature file with a scenario that has no @id tag
    When: parse_feature is called
    Then: The scenario is not included in top_level_examples
    """
    feature_file = tmp_path / "no-id.feature"
    feature_file.write_text(
        "Feature: No Id\n\n"
        "  Example: No id here\n"
        "    Given something\n"
        "    When something\n"
        "    Then something\n",
        encoding="utf-8",
    )

    result = parse_feature(feature_file, folder_name="no-id")

    assert result.top_level_examples == ()


def test_parsed_feature_all_example_ids_collects_from_rules_and_top_level(
    tmp_path: Path,
) -> None:
    """
    Given: A feature with both rules and top-level examples
    When: all_example_ids is called
    Then: Returns all IDs from both
    """
    feature_file = tmp_path / "mixed.feature"
    feature_file.write_text(
        "Feature: Mixed\n\n"
        "  @id:aaaabbbb\n"
        "  Example: Top level\n"
        "    Given something\n\n"
        "  Rule: Some rule\n\n"
        "    @id:ccccdddd\n"
        "    Example: In rule\n"
        "      Given something else\n",
        encoding="utf-8",
    )

    result = parse_feature(feature_file, folder_name="mixed")

    ids = result.all_example_ids()
    assert ExampleId("aaaabbbb") in ids
    assert ExampleId("ccccdddd") in ids
    assert len(ids) == 2


def test_collect_all_example_ids_delegates_to_all_example_ids(tmp_path: Path) -> None:
    """
    Given: A parsed feature with examples
    When: collect_all_example_ids is called
    Then: Returns the same result as all_example_ids
    """
    feature_file = tmp_path / "feature.feature"
    feature_file.write_text(
        "Feature: Test\n\n  @id:aabbccdd\n  Example: An example\n    Given something\n",
        encoding="utf-8",
    )

    parsed = parse_feature(feature_file, folder_name="feature")
    result = collect_all_example_ids(parsed)

    assert result == parsed.all_example_ids()
    assert ExampleId("aabbccdd") in result
