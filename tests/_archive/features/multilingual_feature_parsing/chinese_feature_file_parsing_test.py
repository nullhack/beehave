"""Tests for multilingual feature parsing — Chinese feature file parsing rule."""

from pathlib import Path

from pytest_beehave.feature_parser import ParsedFeature, parse_feature
from pytest_beehave.models import ExampleId


def _write_chinese_feature(directory: Path) -> Path:
    """Write a minimal Chinese Gherkin feature file to directory."""
    path = directory / "gushi.feature"
    path.write_text(
        "# language: zh-CN\n"
        "功能: 中文功能\n\n"
        "  @id:e5f6a7b8\n"
        "  场景: 一个场景\n"
        "    假设 某事\n"
        "    当 某事发生\n"
        "    那么 某事通过\n",
        encoding="utf-8",
    )
    return path


class TestChineseFeatureFileParsing:
    """Tests for the Chinese feature file parsing Rule."""

    def test_multilingual_feature_parsing_55e4d669(self, tmp_path: Path) -> None:
        """
        Given: a valid Chinese Gherkin feature file
        When: parse_feature is called on that file
        Then: a ParsedFeature is returned with the correct number of examples
        """
        feature_dir = tmp_path / "zhong-wen-gong-neng"
        feature_dir.mkdir()
        feature_file = _write_chinese_feature(feature_dir)
        result = parse_feature(feature_file, folder_name="zhong-wen-gong-neng")
        assert isinstance(result, ParsedFeature)
        assert len(result.top_level_examples) == 1
        assert ExampleId("e5f6a7b8") in result.all_example_ids()
