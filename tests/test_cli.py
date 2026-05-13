from __future__ import annotations

from pathlib import Path

import pytest
from conftest import write_feature, write_test

from beehave.cli import main
from beehave.config import Config
from beehave.generate import generate_stubs


class TestCliGenerate:
    def test_generate_creates_files(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "cli_gen",
            """\
            Feature: CLI Gen
              Scenario: hello
                Given stuff
            """,
        )
        main(["generate", "cli_gen"])
        test_file = tmp_project / "tests" / "features" / "cli_gen" / "default_test.py"
        assert test_file.exists()

    def test_generate_missing_feature_exits(self, tmp_project: Path) -> None:
        with pytest.raises(SystemExit):
            main(["generate", "nonexistent"])


class TestCliCheck:
    def test_check_clean_exits_zero(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "cli_chk",
            """\
            Feature: CLI Chk
              Scenario: hello
                Given stuff
            """,
        )
        generate_stubs("cli_chk", config)
        main(["check", "cli_chk"])

    def test_check_violation_exits_one(
        self, tmp_project: Path, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        write_feature(
            tmp_project,
            "cli_bad",
            """\
            Feature: CLI Bad
              Scenario: broken
                Given the hive has <amount> nectar
            """,
        )
        generate_stubs("cli_bad", config)
        write_test(
            tmp_project,
            "cli_bad",
            "default_test.py",
            """\
            from hypothesis import given, strategies as st

            @given(amount=st.integers())
            def test_broken(amount):
                assert True
            """,
        )
        with pytest.raises(SystemExit) as exc_info:
            main(["check", "cli_bad"])
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "missing-placeholder" in captured.out

    def test_check_all_no_args(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "cli_all",
            """\
            Feature: CLI All
              Scenario: hello
                Given stuff
            """,
        )
        generate_stubs("cli_all", config)
        main(["check"])

    def test_check_warning_only_exits_zero(
        self, tmp_project: Path, config: Config
    ) -> None:
        write_feature(
            tmp_project,
            "cli_warn",
            """\
            Feature: CLI Warn
              Scenario: top

              Rule: Sub
                Scenario: sub
                  Given stuff
            """,
        )
        generate_stubs("cli_warn", config)
        write_feature(
            tmp_project,
            "cli_warn",
            """\
            Feature: CLI Warn
              Scenario: top

              Scenario: sub
                Given stuff
            """,
        )
        generate_stubs("cli_warn", config)
        main(["check", "cli_warn"])


class TestCliClean:
    def test_clean_removes_stub(
        self, tmp_project: Path, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        write_feature(
            tmp_project,
            "cli_cln",
            """\
            Feature: CLI Cln
              Scenario: keep
                Given stuff
            """,
        )
        generate_stubs("cli_cln", config)
        write_test(
            tmp_project,
            "cli_cln",
            "default_test.py",
            """\
            def test_keep():
                ...

            def test_unmapped():
                ...
            """,
        )
        main(["clean", "cli_cln"])
        content = (
            tmp_project / "tests" / "features" / "cli_cln" / "default_test.py"
        ).read_text()
        assert "test_unmapped" not in content


class TestCliList:
    def test_list_shows_features(
        self, tmp_project: Path, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        write_feature(
            tmp_project,
            "list1",
            """\
            Feature: List One
              Scenario: hello
                Given stuff
            """,
        )
        write_feature(
            tmp_project,
            "list2",
            """\
            Feature: List Two
              Scenario: world
                Given stuff
            """,
        )
        main(["list"])
        captured = capsys.readouterr()
        assert "list1: List One" in captured.out
        assert "list2: List Two" in captured.out

    def test_list_verbose(
        self, tmp_project: Path, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        write_feature(
            tmp_project,
            "lv",
            """\
            Feature: List Verbose
              Scenario: hello
                Given stuff
            """,
        )
        generate_stubs("lv", config)
        main(["list", "--verbose"])
        captured = capsys.readouterr()
        assert "scenarios:" in captured.out
        assert "stubs:" in captured.out

    def test_list_empty_exits_zero(
        self, tmp_project: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        main(["list"])
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_list_nested_feature(
        self, tmp_project: Path, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        write_feature(
            tmp_project,
            "nested/inner",
            """\
            Feature: Nested Inner
              Scenario: hello
                Given stuff
            """,
        )
        main(["list"])
        captured = capsys.readouterr()
        assert "nested/inner: Nested Inner" in captured.out
