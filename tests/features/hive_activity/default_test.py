import pytest

from hypothesis import given, example, strategies as st


@pytest.mark.skip(reason="not implemented")
@example(nectar=100, rate=20, hours=8, honey=80)
@example(nectar=200, rate=25, hours=12, honey=150)
@example(nectar=50, rate=30, hours=6, honey=35)
@given(
    nectar=st.integers(), rate=st.integers(), hours=st.integers(), honey=st.integers()
)
def test_honey_production_from_nectar(nectar, rate, hours, honey): ...
