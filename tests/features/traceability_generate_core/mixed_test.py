def test_traceability_generate_core_c8e2f4a6(tmp_path) -> None:
    """Generate skips matched scenarios and creates stubs only for orphans.

    Given a .feature file with three scenarios where two have matching test functions and one is an orphan
    When the developer runs beehave generate
    Then the orphan scenario gets a test stub created
    And the two matched scenarios are skipped with a warning
    """
    from beehave.cli import _find_orphan_scenarios

    feature_text = (
        "Feature: Test\n"
        "  Rule: R1\n"
        "    @id:id1aaaaa\n"
        "    Example: First scenario\n"
        "      Given something\n"
        "    @id:id2bbbbb\n"
        "    Example: Second scenario\n"
        "      Given something\n"
        "    @id:id3ccccc\n"
        "    Example: Third scenario\n"
        "      Given something\n"
    )
    feature_file = tmp_path / "test.feature"
    feature_file.write_text(feature_text)

    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "def test_first_scenario_id1aaaaa():\n"
        "    ...\n"
        "\n"
        "def test_second_scenario_id2bbbbb():\n"
        "    ...\n"
    )

    orphans = _find_orphan_scenarios(str(feature_file), str(test_dir))

    assert len(orphans) == 1
    assert orphans[0].name.value == "Third scenario"
    assert orphans[0].id_tag.value == "id3ccccc"
