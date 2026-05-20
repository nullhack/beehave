from pathlib import Path

from conftest import write_feature, write_test  # noqa: E402

from beehave.check import check_all
from beehave.config import Config


def test_quoted_placeholder_not_captured_as_literal(
    tmp_project: Path, config: Config
) -> None:
    write_feature(
        tmp_project,
        "case_insensitive_matching/case_insensitive_matching",
        """\
    Feature: Case Insensitive Matching

      Rule: Quoted Placeholder Not Double Captured

        Scenario: quoted placeholder not captured as literal
          Given a dog named "<name>"
    """,
    )

    write_test(
        tmp_project,
        "case_insensitive_matching",
        "quoted_placeholder_not_double_captured_test.py",
        """\
        def test_quoted_placeholder_not_captured_as_literal():
            name
        """,
    )

    violations = check_all(config)

    ml_violations = [v for v in violations if v.error_type == "missing-literal"]
    assert len(ml_violations) == 0, (
        f"expected 0 missing-literal violations "
        f"('<name>' inside quotes should not be captured as a literal), "
        f"got {len(ml_violations)}: {[(v.error_type, v.message) for v in violations]}"
    )

    mp_violations = [v for v in violations if v.error_type == "missing-placeholder"]
    assert len(mp_violations) == 0, (
        f"expected 0 missing-placeholder violations "
        f"(placeholder <name> matched case-insensitively by body 'name'), "
        f"got {len(mp_violations)}: {[(v.error_type, v.message) for v in violations]}"
    )


def test_non_placeholder_quoted_content_captured(
    tmp_project: Path, config: Config
) -> None:
    write_feature(
        tmp_project,
        "case_insensitive_matching/case_insensitive_matching",
        """\
    Feature: Case Insensitive Matching

      Rule: Quoted Placeholder Not Double Captured

        Scenario: non placeholder quoted content captured
          Given a phone number "[PHONE]"
    """,
    )

    write_test(
        tmp_project,
        "case_insensitive_matching",
        "quoted_placeholder_not_double_captured_test.py",
        """\
        def test_non_placeholder_quoted_content_captured():
            "[PHONE]"
        """,
    )

    violations = check_all(config)

    ml_violations = [v for v in violations if v.error_type == "missing-literal"]
    assert len(ml_violations) == 0, (
        f"expected 0 missing-literal violations "
        f"('[PHONE]' inside quotes should be captured as a literal and "
        f"match the body's '[PHONE]'), "
        f"got {len(ml_violations)}: {[(v.error_type, v.message) for v in violations]}"
    )
