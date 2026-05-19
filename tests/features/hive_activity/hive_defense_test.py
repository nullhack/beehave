import pytest

from hypothesis import given, strategies as st


@pytest.mark.skip(reason="not implemented")
@given(scent=st.text(), outcome=st.text())
def test_guard_bee_inspects_visitor(scent, outcome): ...
