from pathlib import Path

from conftest import write_feature, write_test  # noqa: E402

from beehave.check import check_all
from beehave.config import Config


def test_string_literal_matches_lowercase_constant(
    tmp_project: Path, config: Config
) -> None:
    write_feature(
        tmp_project,
        "case_insensitive_matching/case_insensitive_matching",
        """\
    Feature: Case Insensitive Matching

      Rule: Literal Matching Case Insensitive

        Scenario: string literal matches lowercase constant
          Given a dog named "Rex"
    """,
    )

    write_test(
        tmp_project,
        "case_insensitive_matching",
        "literal_matching_case_insensitive_test.py",
        """\
        def test_string_literal_matches_lowercase_constant():
            "rex"
        """,
    )

    violations = check_all(config)

    ml_violations = [v for v in violations if v.error_type == "missing-literal"]
    assert len(ml_violations) == 0, (
        f"expected 0 missing-literal violations (case-insensitive match: "
        f"'Rex' should match 'rex'), "
        f"got {len(ml_violations)}: {[(v.error_type, v.message) for v in violations]}"
    )


def test_string_literal_matches_uppercase_constant(): ...


def test_numeric_literal_matches_stringified_decimal(): ...
