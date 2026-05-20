import pytest

from hypothesis import given, strategies as st


@pytest.mark.skip(reason="not implemented")
@given(amount=st.text())
def test_worker_builds_a_hexagonal_cell(amount): ...
