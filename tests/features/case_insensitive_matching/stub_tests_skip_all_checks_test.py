from hypothesis import given, strategies as st


@given(Dog=st.text())
def test_stub_test_produces_no_violations(Dog): ...
