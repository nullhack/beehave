def test_traceability_fix_clean_6f1e9d4c(tmp_path, monkeypatch) -> None:
    """Clean requires interactive confirmation.

    Given 3 orphan test functions with no matching .feature scenarios
    When the developer runs beehave clean
    Then the developer is prompted "Remove 3 orphan tests? [y/N]"
    And if yes, the functions are deleted from their files
    """
    from beehave.cli import clean

    # Set up feature file with only 1 scenario
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "clean_test.feature"
    feature_file.write_text(
        "Feature: Clean Test\n"
        "  Rule: R1\n"
        "    @id:keepth01\n"
        "    Example: Keep this scenario\n"
        "      Given something\n"
    )

    # Set up test file with 4 functions (1 matching, 3 orphans)
    test_dir = tmp_path / "tests" / "features" / "clean_test"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "from beehave.decorators import Given\n"
        "\n"
        "\n"
        '@Given("something")\n'
        "def test_keep_this_keepth01():\n"
        "    ...\n"
        "\n"
        "\n"
        "def test_orphan_one_orphn001():\n"
        "    ...\n"
        "\n"
        "\n"
        "def test_orphan_two_orphn002():\n"
        "    ...\n"
        "\n"
        "\n"
        "def test_orphan_three_orphn003():\n"
        "    ...\n"
    )

    prompts = []

    def mock_input(prompt):
        prompts.append(prompt)
        return "y"

    monkeypatch.setattr("beehave.cli._is_interactive", lambda: True)
    monkeypatch.setattr("builtins.input", mock_input)
    monkeypatch.chdir(tmp_path)

    clean("clean_test")

    # Should have prompted
    assert len(prompts) == 1
    assert "Remove 3 orphan tests? [y/N]" in prompts[0]

    # Orphan functions should be deleted
    content = test_file.read_text()
    assert "test_keep_this_keepth01" in content
    assert "orphn001" not in content
    assert "orphn002" not in content
    assert "orphn003" not in content


def test_traceability_fix_clean_a3b8c5d2(tmp_path, monkeypatch) -> None:
    """Clean skips confirmation with --force.

    When the developer runs beehave clean --force
    Then orphan test functions are deleted without confirmation prompt
    """
    from beehave.cli import clean

    # Set up feature file with only 1 scenario
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "force_test.feature"
    feature_file.write_text(
        "Feature: Force Test\n"
        "  Rule: R1\n"
        "    @id:keepth02\n"
        "    Example: Keep this scenario\n"
        "      Given something\n"
    )

    # Set up test file with 2 functions (1 matching, 1 orphan)
    test_dir = tmp_path / "tests" / "features" / "force_test"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "from beehave.decorators import Given\n"
        "\n"
        "\n"
        '@Given("something")\n'
        "def test_keep_this_keepth02():\n"
        "    ...\n"
        "\n"
        "\n"
        "def test_orphan_func_orphn004():\n"
        "    ...\n"
    )

    prompts = []

    def mock_input(prompt):
        prompts.append(prompt)
        return "y"

    monkeypatch.setattr("beehave.cli._is_interactive", lambda: True)
    monkeypatch.setattr("builtins.input", mock_input)
    monkeypatch.chdir(tmp_path)

    clean("force_test", force=True)

    # Should NOT have prompted
    assert len(prompts) == 0

    # Orphan function should be deleted
    content = test_file.read_text()
    assert "test_keep_this_keepth02" in content
    assert "orphn004" not in content
