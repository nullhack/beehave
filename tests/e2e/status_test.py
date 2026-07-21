from __future__ import annotations


def write_feature_text(pytester, basename: str, text: str) -> str:
    dst = pytester.path / "docs" / "features" / basename
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)
    return str(dst)


def write_py_stub(pytester, stem: str) -> str:
    dst = pytester.path / "tests" / "features" / f"{stem}_test.py"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("")
    return str(dst)


def run_beehave_status(pytester, *args: str) -> int:
    return pytester.run("beehave", "status", *args).ret


def status_stdout(pytester) -> str:
    result = pytester.run("beehave", "status")
    return "\n".join(result.outlines)


def test_status_exits_zero_when_features_dir_exists(pytester) -> None:
    write_feature_text(pytester, "a.feature", "Feature: A\nScenario: aaaaa\nGiven x\n")
    assert run_beehave_status(pytester) == 0


def test_status_reports_feature_file_count(pytester) -> None:
    write_feature_text(pytester, "a.feature", "Feature: A\nScenario: aaaaa\nGiven x\n")
    write_feature_text(pytester, "b.feature", "Feature: B\nScenario: bbbbb\nGiven x\n")
    stdout = status_stdout(pytester)
    assert "2" in stdout
    assert "feature" in stdout.lower()


def test_status_reports_emitted_skeleton_count(pytester) -> None:
    write_feature_text(pytester, "a.feature", "Feature: A\nScenario: aaaaa\nGiven x\n")
    write_py_stub(pytester, "a_default")
    write_py_stub(pytester, "a_other")
    stdout = status_stdout(pytester)
    assert "2" in stdout
    assert "skeleton" in stdout.lower()


def test_status_exits_two_when_features_dir_missing(pytester) -> None:
    assert run_beehave_status(pytester) == 2
