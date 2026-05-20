from pathlib import Path

from conftest import write_feature, write_test  # noqa: E402
from hypothesis import HealthCheck, given, settings, strategies as st

from beehave.check import check_all
from beehave.config import Config


@given(Dog=st.text())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_placeholder_matches_lowercase_body_name(
    Dog: str, tmp_project: Path, config: Config
) -> None:
    write_feature(
        tmp_project,
        "case_insensitive_matching/case_insensitive_matching",
        """\
    Feature: Case Insensitive Matching

      Rule: Placeholder Matching Case Insensitive

        Scenario: placeholder matches lowercase body name
          Given a <Dog> barks
    """,
    )

    write_test(
        tmp_project,
        "case_insensitive_matching",
        "placeholder_matching_case_insensitive_test.py",
        """\
        from hypothesis import given, strategies as st

        @given(Dog=st.text())
        def test_placeholder_matches_lowercase_body_name(Dog):
            dog
        """,
    )

    violations = check_all(config)

    mp_violations = [v for v in violations if v.error_type == "missing-placeholder"]
    assert len(mp_violations) == 0, (
        f"expected 0 missing-placeholder violations (case-insensitive), "
        f"got {len(mp_violations)}: {[(v.error_type, v.message) for v in violations]}"
    )


@given(Dog=st.text())
def test_placeholder_matches_uppercase_body_name(Dog): ...


@given(Dog=st.text())
def test_placeholder_matches_mixed_case_body_name(Dog): ...


@given(Dog=st.text())
def test_placeholder_does_not_match_different_identifier(Dog): ...
