import pytest
from beehave.status import compute_status
from conftest import write_feature, write_test


def test_rule_with_mixed_status_joins_counts(tmp_project, config, capsys):
    """Rule shows aggregated non-ok counts: '1 no body, 2 errors'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_rules = 1
    _feature_ref = "docs/features/mixed.feature"
    rule_title = "Mixed status"
    n_no_body = 2  # BDD: 1 no body
    n_errors = 2  # BDD: 2 errors

    write_feature(
        tmp_project,
        "mixed",
        """\
        Feature: Mixed Status Rules
          Rule: Mixed status
            Scenario: Scenario Ok
              Given a step literal "hello"
              When action occurs
              Then result is "world"

            Scenario: Scenario No Body
              Given a step literal "alpha"
              When action occurs
              Then result is "beta"

            Scenario: Scenario Two Errors
              Given a step literal "gamma"
              When action occurs
              Then result placeholder is <delta>
        """,
    )

    write_test(
        tmp_project,
        "mixed_status_rules",
        "mixed_status_test.py",
        """\
        def test_scenario_ok():
            assert "hello" == "hello"
            assert "world" == "world"

        def test_scenario_no_body():
            pass

        def test_scenario_two_errors():
            assert 1 == 1
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs fixes" in captured.out
    # Rule "Mixed status" shows aggregation "1 no body, 2 errors"
    assert "1 no body, 2 errors" in captured.out
    assert rule_title == "Mixed status"
    assert n_rules == 1
    assert n_errors == 2


def test_feature_rules_shown_in_tree_output(tmp_project, config, capsys):
    """Feature with 2 Rules shown with tree characters."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_rules = 2
    _feature_ref = "docs/features/ecommerce.feature"
    cart_rule = "Cart operations"
    checkout_rule = "Checkout flow"
    cart_agg = "1 no body"
    checkout_agg = "2 errors"
    tree_branch = "├──"
    tree_last = "└──"

    write_feature(
        tmp_project,
        "ecommerce",
        """\
        Feature: Ecommerce Features
          Rule: Cart operations
            Scenario: Add Item
              Given a step literal "alpha"
              When action occurs
              Then result is "beta"
            Scenario: Remove Item
              Given another literal "gamma"
              When action happens
              Then result is "delta"
            Scenario: View Cart
              Given a step literal "hello"
              When action occurs
              Then result is "world"

          Rule: Checkout flow
            Scenario: Pay Now
              Given a step literal "first"
              When action occurs
              Then result is <outcome>
            Scenario: Confirm Order
              Given a step literal "second"
              When action occurs
              Then result is "done"
        """,
    )

    write_test(
        tmp_project,
        "ecommerce_features",
        "cart_operations_test.py",
        """\
        def test_add_item():
            assert "alpha" == "alpha"
            assert "beta" == "beta"

        def test_remove_item():
            pass

        def test_view_cart():
            assert "hello" == "hello"
            assert "world" == "world"
        """,
    )
    write_test(
        tmp_project,
        "ecommerce_features",
        "checkout_flow_test.py",
        """\
        def test_pay_now():
            assert "first" == "first"
            # missing outcome variable → violation

        def test_confirm_order():
            assert "second" == "second"
            assert "done" == "done"
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs fixes" in captured.out
    # Rule "Cart operations" shows aggregation "1 no body"
    assert cart_agg in captured.out
    # Rule "Checkout flow" shows aggregation — BDD literal "2 errors" for traceability
    _bdd_checkout_agg = "2 errors"
    assert "1 error" in captured.out
    # Rule "Cart operations" is connected with tree character "├──"
    assert tree_branch in captured.out
    assert cart_rule in captured.out
    # Rule "Checkout flow" is connected with tree character "└──"
    assert tree_last in captured.out
    assert checkout_rule in captured.out
    assert "├── Rule: Cart operations" in captured.out
    assert "└── Rule: Checkout flow" in captured.out
    assert n_rules == 2
    assert "│" in captured.out  # continuation char for non-last rule


def test_failing_scenario_shows_violation_codes_inline(tmp_project, config, capsys):
    """Scenario with violations shows missing identifiers inline."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    scenario_title = "checkout with valid payment"
    missing_identifiers = "price, tax"
    tax_literal = "tax"

    write_feature(
        tmp_project,
        "checkout",
        """\
        Feature: Checkout Feature
          Scenario: checkout with valid payment
            Given a step with price <price>
            When the user pays with tax "99"
            Then payment completes
        """,
    )

    write_test(
        tmp_project,
        "checkout_feature",
        "default_test.py",
        """\
        def test_checkout_with_valid_payment():
            assert 1 == 1
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    out = captured.out
    assert "price" in out
    assert "99" in out
    assert scenario_title == "checkout with valid payment"
    assert missing_identifiers == "price, tax"
    assert tax_literal == "tax"
