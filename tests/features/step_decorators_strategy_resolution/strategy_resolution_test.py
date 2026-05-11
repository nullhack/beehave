from hypothesis import strategies as st

from beehave.strategies import resolve_strategy


def test_strategy_resolution_2c5f1d7e() -> None:
    """Module-level variable resolves a placeholder.

    Given a module with "initial = st.integers(min_value=0)"
    And a step "a user with balance <initial>"
    When @Given processes the step at import time
    Then <initial> resolves to the module-level st.integers(min_value=0)
    """
    import types

    test_module = types.ModuleType("test_module")
    test_module.initial = st.integers(min_value=0)

    result = resolve_strategy("initial", test_module)
    assert result is test_module.initial


def test_strategy_resolution_7a3e8b4c() -> None:
    """@Example value type infers strategy when no module variable exists.

    Given a step "the user spends <amount>" with no module-level "amount"
    And @Example(amount=30)
    When @Given processes the step at import time
    Then <amount> resolves to st.integers() (inferred from int type)
    """
    import types

    test_module = types.ModuleType("test_module")
    examples = {"amount": 30}

    result = resolve_strategy("amount", test_module, examples=examples)
    from hypothesis import find

    generated = find(result, lambda x: True)
    assert isinstance(generated, int)


def test_strategy_resolution_d6f29013() -> None:
    """Unresolved placeholder falls back to st.integers().

    Given a step "the result is <output>" with no module variable and no @Example
    When @Given processes the step at import time
    Then <output> resolves to st.integers() as fallback
    """
    import types

    test_module = types.ModuleType("test_module")

    result = resolve_strategy("output", test_module)
    from hypothesis import find

    generated = find(result, lambda x: True)
    assert isinstance(generated, int)
