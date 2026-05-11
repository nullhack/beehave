def test_traceability_generate_core_1d9b5c4a(tmp_path) -> None:
    """Generate is idempotent — skips scenarios that already have matching test functions.

    Given a test file that already has a function for @id:kx7m2p9q
    When beehave generate encounters the same @id
    Then it skips with a warning "function for @id:kx7m2p9q already exists"
    """
    from beehave.cli import _find_orphan_scenarios

    # Test file already has a function for @id:kx7m2p9q
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "default_test.py"
    original_content = "def test_some_scenario_kx7m2p9q():\n    ...\n"
    test_file.write_text(original_content)

    feature_text = (
        "Feature: Test\n"
        "  Rule: R1\n"
        "    @id:kx7m2p9q\n"
        "    Example: Some scenario\n"
        "      Given something\n"
    )
    feature_file = tmp_path / "test.feature"
    feature_file.write_text(feature_text)

    orphans = _find_orphan_scenarios(str(feature_file), str(test_dir))

    # No orphans found — the scenario already has a matching test function
    assert len(orphans) == 0

    # File is unchanged
    assert test_file.read_text() == original_content
