from __future__ import annotations

import shutil
from pathlib import Path

HIVE_ACTIVITY_FEATURE = "hive_activity.feature"
COMB_CONSTRUCTION_FEATURE = "comb_construction.feature"
TITLE_VALIDATION_FEATURE = "title_validation.feature"
STATUS_COMMAND_FEATURE = "status_command.feature"
CASE_INSENSITIVE_MATCHING_FEATURE = "case_insensitive_matching.feature"

DEFAULT_GROUP_SUFFIX = "default"
EMISSION_DIR = "tests/features"


def copy_feature_into_pytester(pytester, basename: str) -> str:
    src = Path(__file__).resolve().parents[2] / "docs" / "features" / basename
    dst = pytester.path / "docs" / "features" / basename
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    return str(dst)


def write_feature_text(pytester, basename: str, text: str) -> str:
    dst = pytester.path / "docs" / "features" / basename
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)
    return str(dst)


def run_beehave_generate(pytester, *args: str) -> int:
    return pytester.run("beehave", "generate", *args).ret


def read_emitted_py(pytester, stem: str) -> str:
    path = pytester.path / EMISSION_DIR / f"{stem}_test.py"
    if not path.exists():
        return ""
    return path.read_text()


def list_emitted_stems(pytester) -> list[str]:
    emission = pytester.path / EMISSION_DIR
    if not emission.exists():
        return []
    stems: list[str] = []
    for path in emission.glob("*_test.py"):
        name = path.name
        if name.endswith("_test.py"):
            stems.append(name[: -len("_test.py")])
    return sorted(stems)


def test_emits_py_for_default_group_and_each_rule(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    run_beehave_generate(pytester)
    stems = list_emitted_stems(pytester)
    assert "hive_activity_default" in stems
    assert "hive_activity_hive_defense" in stems
    assert "hive_activity_hive_foraging" in stems


def test_always_emits_py_file_for_every_rule_and_default(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    exit_code = run_beehave_generate(pytester)
    assert exit_code == 0
    stems = list_emitted_stems(pytester)
    assert len(stems) >= 3
    for stem in stems:
        assert read_emitted_py(pytester, stem) != ""


def test_emits_py_skeleton_only_when_py_absent(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    run_beehave_generate(pytester)
    first_emission = read_emitted_py(pytester, "hive_activity_default")
    pytester.run("beehave", "generate")
    second_emission = read_emitted_py(pytester, "hive_activity_default")
    assert first_emission == second_emission


def test_scenario_title_emits_test_underscore_slug_function(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    run_beehave_generate(pytester)
    py = read_emitted_py(pytester, "hive_activity_hive_defense")
    assert "def test_guard_bee_inspects_visitor" in py


def test_function_name_carries_no_uppercase_and_collapses_whitespace(pytester) -> None:
    feature_text = (
        "Feature: Whitespace\n"
        "Scenario: MixedCase   Title With   Spaces\n"
        "Given anything\n"
    )
    write_feature_text(pytester, "whitespace.feature", feature_text)
    run_beehave_generate(pytester)
    py = read_emitted_py(pytester, "whitespace_default")
    assert "def test_mixedcase_title_with_spaces" in py


def test_feature_background_steps_appear_in_every_emitted_scenario(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    run_beehave_generate(pytester)
    default_py = read_emitted_py(pytester, "hive_activity_default")
    defense_py = read_emitted_py(pytester, "hive_activity_hive_defense")
    foraging_py = read_emitted_py(pytester, "hive_activity_hive_foraging")
    background_text = "the hive is active"
    assert background_text in default_py
    assert background_text in defense_py
    assert background_text in foraging_py


def test_rule_background_steps_appear_only_in_that_rule_scenarios(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    run_beehave_generate(pytester)
    defense_py = read_emitted_py(pytester, "hive_activity_hive_defense")
    foraging_py = read_emitted_py(pytester, "hive_activity_hive_foraging")
    default_py = read_emitted_py(pytester, "hive_activity_default")
    rule_background_text = "entrance has 2 guards"
    assert rule_background_text in defense_py
    assert rule_background_text not in foraging_py
    assert rule_background_text not in default_py


def test_feature_tags_surface_as_pytestmark_in_py(pytester) -> None:
    feature_text = (
        "@unique_tag_marker\n"
        "Feature: Tagged\n"
        "Scenario: tagged scenario\n"
        "Given anything\n"
    )
    write_feature_text(pytester, "tagged.feature", feature_text)
    run_beehave_generate(pytester)
    py_text = read_emitted_py(pytester, "tagged_default")
    assert "pytestmark = [pytest.mark.unique_tag_marker]" in py_text


def test_scenario_tags_surface_as_decorator_marks(pytester) -> None:
    feature_text = (
        "Feature: Scenario Tags\n@fast\nScenario: tagged scenario\nGiven anything\n"
    )
    write_feature_text(pytester, "sctags.feature", feature_text)
    run_beehave_generate(pytester)
    py_text = read_emitted_py(pytester, "sctags_default")
    assert "@pytest.mark.fast" in py_text


def test_step_docstring_surfaces_as_body_local_var(pytester) -> None:
    feature_text = (
        "Feature: Docstring Surfacing\n"
        "Scenario: scenario with docstring\n"
        "Given anything\n"
        '"""\n'
        "unique docstring marker text\n"
        '"""\n'
    )
    write_feature_text(pytester, "docstring.feature", feature_text)
    run_beehave_generate(pytester)
    py_text = read_emitted_py(pytester, "docstring_default")
    assert "docstring = 'unique docstring marker text'" in py_text


def test_step_data_table_surfaces_as_body_local_var(pytester) -> None:
    feature_text = (
        "Feature: DataTable Surfacing\n"
        "Scenario: scenario with data table\n"
        "Given anything\n"
        "  | unique_col | value |\n"
        "  | marker     | 1     |\n"
    )
    write_feature_text(pytester, "datatable.feature", feature_text)
    run_beehave_generate(pytester)
    py_text = read_emitted_py(pytester, "datatable_default")
    assert "'unique_col': 'marker'" in py_text
    assert "data_table = " in py_text


def test_generate_creates_tests_features_dir_if_absent(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    assert not (pytester.path / "tests" / "features").exists()
    run_beehave_generate(pytester)
    assert (pytester.path / "tests" / "features").is_dir()


def test_outline_scenario_emits_parametrize_in_py(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    run_beehave_generate(pytester)
    py = read_emitted_py(pytester, "hive_activity_default")
    assert "@pytest.mark.parametrize(" in py
    assert "'nectar'" in py and "'honey'" in py
    assert "('100', '20', '8', '80')," in py


def test_generate_does_not_emit_pyi_files(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    run_beehave_generate(pytester)
    pyi_files = list((pytester.path / EMISSION_DIR).glob("*_test.pyi"))
    assert pyi_files == []
