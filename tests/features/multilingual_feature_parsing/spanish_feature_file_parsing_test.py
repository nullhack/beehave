"""Tests for multilingual feature parsing — Spanish feature file parsing rule."""

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
        "  Ejemplo: Un ejemplo\n"
        "    Dado algo\n"
        "    Cuando algo ocurre\n"
        "    Entonces algo pasa\n",
        encoding="utf-8",
    )
    return path


class TestSpanishFeatureFileParsing:
    """Tests for the Spanish feature file parsing Rule."""

    def test_multilingual_feature_parsing_e1081346(self, tmp_path: Path) -> None:
        """
        Given: a valid Spanish Gherkin feature file
        When: parse_feature is called on that file
        Then: a ParsedFeature is returned with the correct number of examples
        """
        feature_dir = tmp_path / "mi-funcionalidad"
        feature_dir.mkdir()
        feature_file = _write_spanish_feature(feature_dir)
        result = parse_feature(feature_file, folder_name="mi-funcionalidad")
        assert isinstance(result, ParsedFeature)
        assert len(result.top_level_examples) == 1
        assert ExampleId("a1b2c3d4") in result.all_example_ids()
