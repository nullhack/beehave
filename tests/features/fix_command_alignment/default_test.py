"""Test stubs for fix_command_alignment feature.

Generated from: docs/features/fix_command_alignment.feature
Rule: Diff-based alignment correctly identifies insertions and deletions
Rule: Diff-based alignment distinguishes text changes from positional shifts
Rule: Fix alignment results are idempotent
"""

from beehave.cli import _align_steps, fix


def test_fix_command_alignment_a1c3e5f7(tmp_path, monkeypatch) -> None:
    """Step inserted mid-scenario produces a single insertion proposal.

    Given a .feature scenario with steps "Given setup" "Then verify"
    And a test with decorators @Given("setup") @Then("verify")
    When the developer inserts "When action" between setup and verify in the .feature file
    And runs beehave fix --dry-run
    Then fix proposes 1 insertion for "When action"
    And does not propose any text replacements for existing decorators
    """
    # Feature file has 3 steps (action was inserted between setup and verify)
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "align_insert.feature"
    feature_file.write_text(
        "Feature: Align Insert\n"
        "  Rule: R1\n"
        "    @id:a1c3e5f7\n"
        "    Example: Step inserted\n"
        "      Given setup\n"
        "      When action\n"
        "      Then verify\n"
    )

    # Test file has only 2 decorators (missing "When action")
    test_dir = tmp_path / "tests" / "features" / "align_insert"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "from beehave.decorators import Given, Then\n"
        "\n"
        "\n"
        "@Given('setup')\n"
        "@Then('verify')\n"
        "def test_step_inserted_a1c3e5f7():\n"
        "    ...\n"
    )

    monkeypatch.chdir(tmp_path)

    # Existing decorators match by content — no text replacements needed
    # Exactly 1 insertion: "When action"
    mismatches, additions = _align_steps(str(feature_file), str(test_dir))
    assert len(mismatches) == 0, (
        f"Expected 0 mismatches (existing steps match by content), got {mismatches}"
    )

    assert len(additions) == 1, f"Expected 1 addition, got {len(additions)}"
    assert additions[0]["step_text"] == "action"
    assert additions[0]["keyword"] == "When"


def test_fix_command_alignment_b2d4f6a8(tmp_path, monkeypatch) -> None:
    """Step deleted from mid-scenario produces a single deletion proposal.

    Given a .feature scenario with steps "Given setup" "When action" "Then verify"
    And a test with decorators @Given("setup") @When("action") @Then("verify")
    When the developer removes "When action" from the .feature file
    And runs beehave fix --dry-run
    Then fix proposes 1 deletion for @When("action")
    And does not propose any text replacements for the remaining decorators
    """
    # Feature file has 2 steps (action was removed)
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "align_delete.feature"
    feature_file.write_text(
        "Feature: Align Delete\n"
        "  Rule: R1\n"
        "    @id:b2d4f6a8\n"
        "    Example: Step deleted\n"
        "      Given setup\n"
        "      Then verify\n"
    )

    # Test file still has 3 decorators (action decorator is orphaned)
    test_dir = tmp_path / "tests" / "features" / "align_delete"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "from beehave.decorators import Given, When, Then\n"
        "\n"
        "\n"
        "@Given('setup')\n"
        "@When('action')\n"
        "@Then('verify')\n"
        "def test_step_deleted_b2d4f6a8():\n"
        "    ...\n"
    )

    monkeypatch.chdir(tmp_path)

    result = fix("align_delete", dry_run=True)

    # Should detect the extra @When("action") decorator as a deletion
    assert result is not None, "Expected changes (1 deletion)"

    # Should NOT propose replacing "action" text with "verify" text.
    # Positional comparison wrongly maps step[1]="verify" to dec[1]="action",
    # producing a replace. Content-based alignment recognises both "setup" and
    # "verify" match by content, so no text replacement is needed.
    assert '"verify"' not in result, (
        f"Expected no text replacement for 'verify', got:\n{result}"
    )


def test_fix_command_alignment_c3e5a7b1(tmp_path, monkeypatch) -> None:
    """Changed step text is classified as replace, not insert plus delete.

    Given a .feature scenario with step "When the user deposits <amount>"
    And a test with decorator @When("the user withdraws <amount>")
    When beehave fix compares the feature steps to test decorators
    Then fix classifies the mismatch as a single replace operation
    And the mismatch carries expected "the user deposits <amount>" and actual "the user withdraws <amount>"
    """
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "replace_class.feature"
    feature_file.write_text(
        "Feature: Replace Classification\n"
        "  Rule: R1\n"
        "    @id:c3e5a7b1\n"
        "    Example: Changed text\n"
        "      When the user deposits <amount>\n"
    )

    test_dir = tmp_path / "tests" / "features" / "replace_class"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "from beehave.decorators import When\n"
        "\n"
        "\n"
        "@When('the user withdraws <amount>')\n"
        "def test_changed_text_c3e5a7b1(amount):\n"
        "    ...\n"
    )

    monkeypatch.chdir(tmp_path)

    mismatches, additions = _align_steps(str(feature_file), str(test_dir))
    assert len(mismatches) == 1
    m = mismatches[0]
    assert m["new_text"] == "the user deposits <amount>"
    assert m["old_text"] == "the user withdraws <amount>"

    # The mismatch should be classified as "replace", not insert+delete
    assert m.get("operation") == "replace", (
        f"Expected operation='replace', got {m.get('operation')}"
    )

    # No insertions or deletions — this is a pure text replacement
    assert len(additions) == 0


def test_fix_command_alignment_d4f6b8c2(tmp_path, monkeypatch) -> None:
    """Steps with similar text are not falsely aligned.

    Given a .feature scenario with steps "Given a user exists" "Given a user is admin"
    And a test with decorators @Given("a user exists") @Given("a user is admin")
    When the developer inserts "When the user logs in" between them in the .feature file
    And runs beehave fix --dry-run
    Then fix proposes 1 insertion for "When the user logs in"
    And does not propose text replacements for the existing similar decorators
    """
    # Feature has 3 steps (new step inserted between similar ones)
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "similar_steps.feature"
    feature_file.write_text(
        "Feature: Similar Steps\n"
        "  Rule: R1\n"
        "    @id:d4f6b8c2\n"
        "    Example: Similar text\n"
        "      Given a user exists\n"
        "      When the user logs in\n"
        "      Given a user is admin\n"
    )

    # Test has 2 decorators matching the outer steps by content
    test_dir = tmp_path / "tests" / "features" / "similar_steps"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "from beehave.decorators import Given\n"
        "\n"
        "\n"
        "@Given('a user exists')\n"
        "@Given('a user is admin')\n"
        "def test_similar_text_d4f6b8c2():\n"
        "    ...\n"
    )

    monkeypatch.chdir(tmp_path)

    # Both existing decorators match by content — no text replacements needed
    # Exactly 1 insertion: "When the user logs in"
    mismatches, additions = _align_steps(str(feature_file), str(test_dir))
    assert len(mismatches) == 0, f"Expected 0 mismatches, got {mismatches}"

    assert len(additions) == 1, f"Expected 1 addition, got {len(additions)}"
    assert additions[0]["step_text"] == "the user logs in"
    assert additions[0]["keyword"] == "When"


def test_fix_command_alignment_e5a7c9d3(tmp_path, monkeypatch) -> None:
    """Running fix after applying changes reports no mismatches.

    Given a .feature scenario with 3 steps and a test with 2 matching decorators and 1 mismatched decorator
    When the developer runs beehave fix and applies all proposed changes
    And then runs beehave fix again
    Then fix reports no mismatches
    """
    docs_dir = tmp_path / "docs" / "features"
    docs_dir.mkdir(parents=True)
    feature_file = docs_dir / "idempotent.feature"
    feature_file.write_text(
        "Feature: Idempotent\n"
        "  Rule: R1\n"
        "    @id:e5a7c9d3\n"
        "    Example: Idempotent fix\n"
        "      Given setup\n"
        "      When action\n"
        "      Then verify\n"
    )

    # Test has 2 matching decorators — "action" step has no decorator yet
    test_dir = tmp_path / "tests" / "features" / "idempotent"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "default_test.py"
    test_file.write_text(
        "from beehave.decorators import Given, Then\n"
        "\n"
        "\n"
        '@Given("setup")\n'
        '@Then("verify")\n'
        "def test_idempotent_e5a7c9d3():\n"
        "    ...\n"
    )

    monkeypatch.chdir(tmp_path)

    # First run: apply changes
    fix("idempotent")

    # Verify fix produced correct alignment — "action" should have @When decorator
    content = test_file.read_text()
    assert "@When" in content, (
        f"Expected @When decorator for 'action' step after fix, got:\n{content}"
    )

    # Second run: should report no mismatches
    result = fix("idempotent", dry_run=True)
    assert result is None, f"Expected no changes on second run, got:\n{result}"
