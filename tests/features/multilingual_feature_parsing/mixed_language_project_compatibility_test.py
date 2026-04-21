"""Tests for multilingual feature parsing — mixed-language project compatibility rule."""

from pathlib import Path

from pytest_beehave.feature_parser import ParsedFeature, parse_feature
from pytest_beehave.models import ExampleId


def _write_spanish_feature(directory: Path) -> Path:
    """Write a minimal Spanish Gherkin feature file to directory."""
    path = directory / "historia.feature"
    path.write_text(
        "# language: es\n"
        "Característica: Mi funcionalidad\n\n"
        "  @id:a1b2c3d4\n"
        "  Escenario: Un escenario\n"
        "    Dado algo\n"
        "    Cuando algo ocurre\n"
        "    Entonces algo pasa\n",
        encoding="utf-8",
    )
    return path


def _write_english_feature(directory: Path) -> Path:
    """Write a minimal English Gherkin feature file to directory."""
    path = directory / "story.feature"
    path.write_text(
        "Feature: My feature\n\n"
        "  @id:e1f2a3b4\n"
        "  Example: An example\n"
        "    Given something\n"
        "    When something happens\n"
        "    Then something passes\n",
        encoding="utf-8",
    )
    return path


class TestMixedLanguageProjectCompatibility:
    """Tests for the Mixed-language project compatibility Rule."""

    def test_multilingual_feature_parsing_3c04262e(self, tmp_path: Path) -> None:
        """
        Given: a project containing a valid Spanish Gherkin feature file and a valid English feature file
        When: parse_feature is called on each file independently
        Then: both files are parsed successfully and return valid ParsedFeature objects
        """
        spanish_dir = tmp_path / "mi-funcionalidad"
        spanish_dir.mkdir()
        english_dir = tmp_path / "my-feature"
        english_dir.mkdir()
        spanish_file = _write_spanish_feature(spanish_dir)
        english_file = _write_english_feature(english_dir)
        spanish_result = parse_feature(spanish_file, folder_name="mi-funcionalidad")
        english_result = parse_feature(english_file, folder_name="my-feature")
        assert isinstance(spanish_result, ParsedFeature)
        assert isinstance(english_result, ParsedFeature)
        assert ExampleId("a1b2c3d4") in spanish_result.all_example_ids()
        assert ExampleId("e1f2a3b4") in english_result.all_example_ids()
