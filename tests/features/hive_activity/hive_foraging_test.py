import pytest

from hypothesis import given, strategies as st

@pytest.mark.skip(reason="not implemented")
@given(name=st.text(), volume=st.text())
def test_forager_returns_with_nectar(name, volume):
    ...

