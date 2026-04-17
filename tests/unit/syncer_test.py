"""Unit tests for pytest_beehave.syncer module."""

from pathlib import Path

import pytest

from pytest_beehave.syncer import (
    _add_orphan_marker,
    _extract_id,
    _find_triple_quote_end,
    _render_data_table,
    _render_examples_table,
    _replace_docstring,
    _sync_completed_feature,
    _sync_one_feature,
    sync_stubs,
)


@pytest.mark.unit
def test_extract_id_returns_none_when_no_id_tag() -> None:
    """
    Given: A list of tags that contain no @id tag
    When: _extract_id is called
    Then: None is returned
    """
    # Given
    tags = [{"name": "@smoke"}, {"name": "@wip"}]
    # When
    result = _extract_id(tags)
    # Then
    assert result is None


@pytest.mark.unit
def test_parse_examples_returns_empty_for_empty_feature(tmp_path: Path) -> None:
    """
    Given: A .feature file with no scenarios
    When: sync_stubs is called
    Then: No stubs are created and no actions are returned
    """
    # Given
    features_dir = tmp_path / "docs" / "features"
    (features_dir / "backlog" / "empty-feature").mkdir(parents=True)
    feature_file = features_dir / "backlog" / "empty-feature" / "empty.feature"
    feature_file.write_text("Feature: Empty\n", encoding="utf-8")
    tests_dir = tmp_path / "tests" / "features"
    # When
    actions = sync_stubs(features_dir, tests_dir)
    # Then
    assert actions == []


@pytest.mark.unit
def test_parse_examples_skips_scenario_without_id_tag(tmp_path: Path) -> None:
    """
    Given: A .feature file with an Example that has no @id tag
    When: sync_stubs is called
    Then: No stubs are created
    """
    # Given
    features_dir = tmp_path / "docs" / "features"
    (features_dir / "backlog" / "my-feature").mkdir(parents=True)
    feature_file = features_dir / "backlog" / "my-feature" / "story.feature"
    feature_file.write_text(
        "Feature: My feature\n"
        "  Example: No id here\n"
        "    Given a condition\n"
        "    When an action\n"
        "    Then an outcome\n",
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests" / "features"
    # When
    actions = sync_stubs(features_dir, tests_dir)
    # Then
    assert actions == []


@pytest.mark.unit
def test_sync_one_feature_updates_existing_test_file(tmp_path: Path) -> None:
    """
    Given: A .feature file whose corresponding test file already exists (in-progress stage)
    When: _sync_one_feature is called
    Then: The test file is updated (not skipped)
    """
    # Given
    feature_file = tmp_path / "story.feature"
    feature_file.write_text(
        "Feature: My feature\n"
        "  @id:aabbccdd\n"
        "  Example: Something\n"
        "    Given g\n"
        "    When w\n"
        "    Then t\n",
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests"
    test_file = tests_dir / "my_feature" / "story_test.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        '"""Tests for story."""\n\nimport pytest\n\n\n'
        "def test_my_feature_aabbccdd() -> None:\n"
        '    """\n    Given: old\n    When: old\n    Then: old\n    """\n'
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )
    # When
    result = _sync_one_feature(feature_file, "my-feature", "in-progress", tests_dir)
    # Then — file was updated (docstring refreshed)
    assert result is not None


@pytest.mark.unit
def test_sync_stubs_skips_non_directory_entries(tmp_path: Path) -> None:
    """
    Given: A stage directory containing a regular file alongside feature folders
    When: sync_stubs is called
    Then: The regular file is ignored and no error is raised
    """
    # Given
    features_dir = tmp_path / "docs" / "features"
    stage_dir = features_dir / "backlog"
    stage_dir.mkdir(parents=True)
    # A stray non-directory file in the stage directory
    (stage_dir / "README.md").write_text("# Backlog\n", encoding="utf-8")
    # A proper feature folder with a valid feature file
    (stage_dir / "my-feature").mkdir()
    (stage_dir / "my-feature" / "story.feature").write_text(
        "Feature: My feature\n"
        "  @id:aabbccdd\n"
        "  Example: Something\n"
        "    Given g\n"
        "    When w\n"
        "    Then t\n",
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests" / "features"
    # When
    actions = sync_stubs(features_dir, tests_dir)
    # Then — only the feature folder produces an action; README.md is silently skipped
    assert len(actions) == 1
    assert "story_test.py" in actions[0]


@pytest.mark.unit
def test_stub_creation_includes_deprecated_marker(tmp_path: Path) -> None:
    """
    Given: A .feature file with a deprecated Example
    When: sync_stubs is called
    Then: The generated stub contains the deprecated marker
    """
    # Given
    features_dir = tmp_path / "docs" / "features"
    (features_dir / "backlog" / "my-feature").mkdir(parents=True)
    feature_file = features_dir / "backlog" / "my-feature" / "story.feature"
    feature_file.write_text(
        "Feature: My feature\n"
        "  @deprecated @id:aabbccdd\n"
        "  Example: Old behaviour\n"
        "    Given g\n"
        "    When w\n"
        "    Then t\n",
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests" / "features"
    # When
    sync_stubs(features_dir, tests_dir)
    # Then — stub uses underscore slug path
    stub = tests_dir / "my_feature" / "story_test.py"
    assert stub.exists()
    assert "@pytest.mark.deprecated" in stub.read_text(encoding="utf-8")


@pytest.mark.unit
def test_parse_examples_returns_empty_for_file_with_no_feature_keyword(
    tmp_path: Path,
) -> None:
    """
    Given: A file with no Feature keyword (e.g., completely empty)
    When: sync_stubs is called with that file
    Then: No stubs are created and no actions are returned
    """
    # Given
    features_dir = tmp_path / "docs" / "features"
    (features_dir / "backlog" / "my-feature").mkdir(parents=True)
    feature_file = features_dir / "backlog" / "my-feature" / "story.feature"
    feature_file.write_text("", encoding="utf-8")  # no Feature keyword
    tests_dir = tmp_path / "tests" / "features"
    # When
    actions = sync_stubs(features_dir, tests_dir)
    # Then
    assert actions == []


@pytest.mark.unit
def test_parse_examples_skips_background_child(tmp_path: Path) -> None:
    """
    Given: A .feature file containing a Background block alongside an Example
    When: sync_stubs is called
    Then: Only the Example with an @id produces a stub; the Background is ignored
    """
    # Given
    features_dir = tmp_path / "docs" / "features"
    (features_dir / "backlog" / "my-feature").mkdir(parents=True)
    feature_file = features_dir / "backlog" / "my-feature" / "story.feature"
    feature_file.write_text(
        "Feature: My feature\n"
        "  Background:\n"
        "    Given a background step\n"
        "  @id:aabbccdd\n"
        "  Example: Something\n"
        "    Given g\n"
        "    When w\n"
        "    Then t\n",
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests" / "features"
    # When
    actions = sync_stubs(features_dir, tests_dir)
    # Then — one action for the Example stub; Background is silently skipped
    assert len(actions) == 1
    assert "story_test.py" in actions[0]


@pytest.mark.unit
def test_sync_one_feature_returns_empty_for_completed_stage_no_test_file(
    tmp_path: Path,
) -> None:
    """
    Given: A .feature file in the completed stage with no existing test file
    When: _sync_one_feature is called
    Then: An empty list is returned (no stub creation for completed features)
    """
    # Given
    feature_file = tmp_path / "story.feature"
    feature_file.write_text(
        "Feature: My feature\n"
        "  @id:aabbccdd\n"
        "  Example: Something\n"
        "    Given g\n"
        "    When w\n"
        "    Then t\n",
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests"
    # When
    result = _sync_one_feature(feature_file, "my-feature", "completed", tests_dir)
    # Then
    assert result == []


@pytest.mark.unit
def test_sync_completed_feature_returns_empty_for_feature_with_no_examples(
    tmp_path: Path,
) -> None:
    """
    Given: A .feature file in the completed stage with no @id-tagged Examples
    When: _sync_completed_feature is called
    Then: An empty list is returned
    """
    # Given
    feature_file = tmp_path / "story.feature"
    feature_file.write_text(
        "Feature: My feature\n",
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests"
    # When
    result = _sync_completed_feature(feature_file, "my-feature", tests_dir)
    # Then
    assert result == []


@pytest.mark.unit
def test_render_data_table_returns_empty_string_for_empty_rows() -> None:
    """
    Given: An empty list of rows
    When: _render_data_table is called
    Then: An empty string is returned
    """
    # Given / When
    result = _render_data_table([])
    # Then
    assert result == ""


@pytest.mark.unit
def test_render_examples_table_returns_empty_string_for_empty_examples() -> None:
    """
    Given: An empty list of examples
    When: _render_examples_table is called
    Then: An empty string is returned
    """
    # Given / When
    result = _render_examples_table([])
    # Then
    assert result == ""


@pytest.mark.unit
def test_render_examples_table_returns_header_only_for_empty_rows() -> None:
    """
    Given: An examples entry with no header and no body rows
    When: _render_examples_table is called
    Then: 'Examples:' is returned
    """
    # Given
    examples = [{"tableHeader": None, "tableBody": []}]
    # When
    result = _render_examples_table(examples)
    # Then
    assert result == "Examples:"


@pytest.mark.unit
def test_replace_docstring_returns_content_unchanged_when_no_match() -> None:
    """
    Given: File content with no matching function definition
    When: _replace_docstring is called
    Then: The content is returned unchanged
    """
    from pytest_beehave.syncer import _Example, _StepLine

    # Given
    content = "def some_other_function() -> None:\n    pass\n"
    example = _Example(
        id_hex="aabbccdd",
        steps=(
            _StepLine(
                keyword="Given", text="a thing", doc_string=None, data_table=None
            ),
        ),
        background_sections=(),
        outline_examples=None,
        deprecated=False,
    )
    # When
    result = _replace_docstring(content, "test_nonexistent_aabbccdd", example)
    # Then
    assert result == content


@pytest.mark.unit
def test_find_triple_quote_end_returns_content_length_for_unterminated_string() -> None:
    """
    Given: Content with an unterminated triple-quoted string
    When: _find_triple_quote_end is called
    Then: len(content) is returned
    """
    # Given
    content = '"""unterminated string without closing quotes'
    # When
    result = _find_triple_quote_end(content, 0, '"""')
    # Then
    assert result == len(content)


@pytest.mark.unit
def test_add_orphan_marker_is_idempotent() -> None:
    """
    Given: File content where the orphan marker is already present before a function
    When: _add_orphan_marker is called again
    Then: The content is returned unchanged (marker not duplicated)
    """
    # Given
    orphan_marker = (
        '@pytest.mark.skip(reason="orphan: no matching @id in .feature files")'
    )
    content = f"{orphan_marker}\ndef test_my_feature_aabbccdd() -> None:\n    pass\n"
    # When
    result = _add_orphan_marker(content, "test_my_feature_aabbccdd")
    # Then
    assert result == content
    assert result.count(orphan_marker) == 1


@pytest.mark.unit
def test_add_orphan_marker_returns_unchanged_when_function_not_found() -> None:
    """
    Given: File content that does not contain the named function
    When: _add_orphan_marker is called
    Then: The content is returned unchanged
    """
    # Given
    content = "def test_some_other_function() -> None:\n    pass\n"
    # When
    result = _add_orphan_marker(content, "test_nonexistent_aabbccdd")
    # Then
    assert result == content
