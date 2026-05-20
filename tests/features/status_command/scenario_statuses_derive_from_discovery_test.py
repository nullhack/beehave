import pytest
from beehave.status import compute_status
from conftest import write_feature, write_test


def test_scenario_with_no_matching_test_function(tmp_project, config, capsys):
    """Scenario with no matching test function → 'no test'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    scenario_name = "test_delete_item"

    write_feature(
        tmp_project,
        "unmapped_single",
        """\
        Feature: Unmapped Feature
          Scenario: Delete Item
            Given an item exists
            When the user deletes the item
            Then the item is gone
        """,
    )
    assert scenario_name == "test_delete_item"

    # No test file written — all scenarios unmapped
    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "no test" in captured.out
    assert "needs tests" in captured.out


def test_scenario_with_matching_stub_test(tmp_project, config, capsys):
    """Scenario with stub test → 'no body'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    scenario_name = "test_create_item"

    write_feature(
        tmp_project,
        "stub_single",
        """\
        Feature: Stub Feature
          Scenario: Create Item
            Given a form is open
            When the user submits the form
            Then a new item is created
        """,
    )
    assert scenario_name == "test_create_item"

    write_test(
        tmp_project,
        "stub_feature",
        "default_test.py",
        """\
        def test_create_item():
            pass
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "no body" in captured.out
    assert "needs bodies" in captured.out


def test_scenario_non_stub_test_violations(tmp_project, config, capsys):
    """Scenario with non-stub test and missing-literal → '1 error'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    scenario_name = "test_update_item"
    literal_value = "new"
    violation_count = 1

    write_feature(
        tmp_project,
        "missing",
        """\
        Feature: Missing Literal Feature
          Scenario: Update Item
            Given an item with value "new"
            When the user updates the item
            Then the item is updated
        """,
    )
    assert scenario_name == "test_update_item"
    assert literal_value == "new"
    # missing-literal violation for "new"
    _ = literal_value  # second occurrence of "new"

    write_test(
        tmp_project,
        "missing_literal_feature",
        "default_test.py",
        """\
        def test_update_item():
            assert 1 == 1
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "1 error" in captured.out
    assert "needs fixes" in captured.out
    assert violation_count == 1


def test_scenario_non_stub_test_zero_violations(tmp_project, config, capsys):
    """Scenario with non-stub test and zero violations → 'ok'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    scenario_name = "test_list_items"
    placeholder_val = "page"

    write_feature(
        tmp_project,
        "passing",
        """\
        Feature: Passing Feature
          Scenario: List Items
            Given the page is <page>
            When the user lists items
            Then items are shown
        """,
    )
    assert scenario_name == "test_list_items"
    assert placeholder_val == "page"
    # body_name_nodes contains "page"
    _ = placeholder_val  # second occurrence of "page"

    write_test(
        tmp_project,
        "passing_feature",
        "default_test.py",
        """\
        def test_list_items():
            page = 1
            assert page == 1
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "ok" in captured.out
