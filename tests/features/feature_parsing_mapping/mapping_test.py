from beehave.parsing import (
    FeatureFile,
    Rule,
    TestModule,
    resolve_all_test_modules,
    resolve_test_module_path,
)


def test_feature_parsing_mapping_2a8f5c1e():
    """Feature with no Rule maps to default_test.py

    Given a .feature file "balance_accounting.feature" with no Rule defined
    When beehave resolves the test module path
    Then it maps to tests/features/balance_accounting/default_test.py
    """
    feature = FeatureFile(name="balance_accounting.feature", rules=[])
    module = resolve_test_module_path(feature.name, None)
    assert isinstance(module, TestModule)
    assert str(module.path) == "tests/features/balance_accounting/default_test.py"


def test_feature_parsing_mapping_7d3b9e6a():
    """Feature with one Rule maps to <rule_name>_test.py

    Given a .feature file "balance_accounting.feature" with Rule "Total calculation"
    When beehave resolves the test module path
    Then it maps to tests/features/balance_accounting/total_calculation_test.py
    """
    feature = FeatureFile(
        name="balance_accounting.feature",
        rules=[Rule(name="Total calculation")],
    )
    module = resolve_test_module_path(feature.name, feature.rules[0])
    assert isinstance(module, TestModule)
    assert (
        str(module.path)
        == "tests/features/balance_accounting/total_calculation_test.py"
    )


def test_feature_parsing_mapping_cbac8dae():
    """Feature with multiple Rules maps to multiple test modules

    Given a .feature file "balance_accounting.feature" with Rules "Total calculation" and "Balance check"
    When beehave resolves the test module paths
    Then it maps to tests/features/balance_accounting/total_calculation_test.py
    And it maps to tests/features/balance_accounting/balance_check_test.py
    """
    feature = FeatureFile(
        name="balance_accounting.feature",
        rules=[Rule(name="Total calculation"), Rule(name="Balance check")],
    )
    modules = resolve_all_test_modules(feature)
    assert len(modules) == 2
    paths = {str(m.path) for m in modules}
    assert "tests/features/balance_accounting/total_calculation_test.py" in paths
    assert "tests/features/balance_accounting/balance_check_test.py" in paths
