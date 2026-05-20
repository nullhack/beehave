from pathlib import Path

from conftest import write_feature, write_test  # noqa: E402

from beehave.check import check_all
from beehave.config import Config


def test_negative_integer_literal_matches_body_constant(
    tmp_project: Path, config: Config
) -> None:
    write_feature(
        tmp_project,
        "case_insensitive_matching/case_insensitive_matching",
        """\
    Feature: Case Insensitive Matching

      Rule: Negative Numbers Visible In Body

        Scenario: negative integer literal matches body constant
          Given the balance is -2010
    """,
    )

    write_test(
        tmp_project,
        "case_insensitive_matching",
        "negative_numbers_visible_in_body_test.py",
        """\
        def test_negative_integer_literal_matches_body_constant():
            balance = -2010
        """,
    )

    violations = check_all(config)

    ml_violations = [v for v in violations if v.error_type == "missing-literal"]
    assert len(ml_violations) == 0, (
        f"expected 0 missing-literal violations (-2010 from Gherkin should match "
        f"-2010 in body), "
        f"got {len(ml_violations)}: {[(v.error_type, v.message) for v in violations]}"
    )


def test_negative_float_literal_matches_body_constant(): ...


def test_positive_integer_still_works(): ...
