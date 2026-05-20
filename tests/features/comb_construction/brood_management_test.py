import pytest

from hypothesis import given, example, strategies as st


@pytest.mark.skip(reason="not implemented")
@given(kind=st.text())
def test_queen_lays_egg_in_cell(kind): ...


@pytest.mark.skip(reason="not implemented")
@example(ambient=28, workers=20, target=35)
@example(ambient=40, workers=15, target=35)
@given(ambient=st.integers(), workers=st.integers(), target=st.integers())
def test_nursery_temperature_regulation(ambient, workers, target): ...
