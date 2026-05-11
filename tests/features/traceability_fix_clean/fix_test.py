def test_traceability_fix_clean_b8e2f6d7(tmp_path, monkeypatch) -> None:
    """Fix corrects decorator text to match .feature.

    Given a test with @Given("a user with an balance <initial>")
    And a .feature step "Given a user with balance <initial>"
    When the developer runs beehave fix
    Then the decorator is corrected to @Given("a user with balance <initial>")
    """
    from beehave.cli import fix

    # Set up feature file
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "fix_text.feature"
    feature_file.write_text(
        "Feature: Fix Text\n"
        "  Rule: R1\n"
        "    @id:b8e2f6d7\n"
        "    Example: Fix text mismatch\n"
        "      Given a user with balance <initial>\n"
    )

    # Set up test file with wrong decorator text
    test_dir = tmp_path / "tests" / "features" / "fix_text"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "from beehave.decorators import Given\n"
        "\n"
        "\n"
        '@Given("a user with an balance <initial>")\n'
        "def test_fix_text_mismatch_b8e2f6d7(initial):\n"
        "    ...\n"
    )

    monkeypatch.chdir(tmp_path)
    fix("fix_text")

    content = test_file.read_text()
    assert '@Given("a user with balance <initial>")' in content
    assert "an balance" not in content


def test_traceability_fix_clean_4a9c3e5f(tmp_path, monkeypatch) -> None:
    """Fix adds missing step decorators.

    Given a .feature scenario with 3 steps but a test with only 2 decorators
    When the developer runs beehave fix
    Then the missing decorator is added with correct step text and keyword
    And the corresponding <placeholder> names are added to the function parameters
    """
    from beehave.cli import fix

    # Set up feature file with 3 steps
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "missing_dec.feature"
    feature_file.write_text(
        "Feature: Missing Decorators\n"
        "  Rule: R1\n"
        "    @id:4a9c3e5f\n"
        "    Example: Missing decorator\n"
        "      Given a user with balance <initial>\n"
        "      When the user deposits <amount>\n"
        "      Then the balance is <expected>\n"
    )

    # Set up test file with only 2 decorators (missing Then)
    test_dir = tmp_path / "tests" / "features" / "missing_dec"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "from beehave.decorators import Given, When, Then\n"
        "\n"
        "\n"
        '@Given("a user with balance <initial>")\n'
        '@When("the user deposits <amount>")\n'
        "def test_missing_decorator_4a9c3e5f(initial, amount):\n"
        "    ...\n"
    )

    monkeypatch.chdir(tmp_path)
    fix("missing_dec")

    content = test_file.read_text()
    # Missing decorator should be added
    assert '@Then("the balance is <expected>")' in content
    # Placeholder params should be added to function signature
    assert "expected" in content


def test_traceability_fix_clean_d2c7a8b1(tmp_path, monkeypatch) -> None:
    """Fix supports dry-run mode.

    When the developer runs beehave fix --dry-run
    Then a diff of proposed changes is shown without modifying any files
    """
    from beehave.cli import fix

    # Set up feature file
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "dryrun.feature"
    feature_file.write_text(
        "Feature: Dry Run\n"
        "  Rule: R1\n"
        "    @id:d2c7a8b1\n"
        "    Example: Dry run mode\n"
        "      Given a user with balance <initial>\n"
    )

    # Set up test file with wrong decorator text
    test_dir = tmp_path / "tests" / "features" / "dryrun"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    original_content = (
        "from beehave.decorators import Given\n"
        "\n"
        "\n"
        '@Given("a user with an balance <initial>")\n'
        "def test_dry_run_mode_d2c7a8b1(initial):\n"
        "    ...\n"
    )
    test_file.write_text(original_content)

    monkeypatch.chdir(tmp_path)
    result = fix("dryrun", dry_run=True)

    # File should NOT be modified
    assert test_file.read_text() == original_content
    # But a diff should be returned
    assert result is not None
    assert "a user with balance <initial>" in result
