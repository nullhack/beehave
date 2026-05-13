from __future__ import annotations

from pathlib import Path

import pytest
from conftest import write_feature, write_test

from beehave.clean import clean_unmapped
from beehave.config import Config
from beehave.generate import generate_stubs


class TestCleanUnmapped:
    def test_removes_stub_silently(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "cln1",
            """\
            Feature: Cln1
              Scenario: keep
                Given stuff
            """,
        )
        generate_stubs("cln1", config)
        write_test(
            tmp_project,
            "cln1",
            "default_test.py",
            """\
            def test_keep():
                ...

            def test_unmapped():
                ...
            """,
        )
        clean_unmapped("cln1", config)
        content = (
            tmp_project / "tests" / "features" / "cln1" / "default_test.py"
        ).read_text()
        assert "test_keep" in content
        assert "test_unmapped" not in content

    def test_warns_on_non_stub(
        self, tmp_project: Path, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        write_feature(
            tmp_project,
            "cln2",
            """\
            Feature: Cln2
              Scenario: keep
                Given stuff
            """,
        )
        generate_stubs("cln2", config)
        write_test(
            tmp_project,
            "cln2",
            "default_test.py",
            """\
            def test_keep():
                ...

            def test_real():
                assert True
            """,
        )
        clean_unmapped("cln2", config)
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "test_real" in captured.out
        content = (
            (tmp_project / "tests" / "cln2" / "default_test.py").read_text()
            if (tmp_project / "tests" / "cln2" / "default_test.py").exists()
            else ""
        )
        test_dir = tmp_project / "tests" / "features" / "cln2" / "default_test.py"
        content = test_dir.read_text()
        assert "test_real" in content

    def test_force_removes_non_stub(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "cln3",
            """\
            Feature: Cln3
              Scenario: keep
                Given stuff
            """,
        )
        generate_stubs("cln3", config)
        write_test(
            tmp_project,
            "cln3",
            "default_test.py",
            """\
            def test_keep():
                ...

            def test_real():
                assert True
            """,
        )
        clean_unmapped("cln3", config, force=True)
        content = (
            tmp_project / "tests" / "features" / "cln3" / "default_test.py"
        ).read_text()
        assert "test_keep" in content
        assert "test_real" not in content

    def test_nonexistent_feature_exits(self, tmp_project: Path, config: Config) -> None:
        with pytest.raises(SystemExit):
            clean_unmapped("nonexistent", config)

    def test_rule_based_clean(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "clnr",
            """\
            Feature: Cln Rule
              Rule: Alpha
                Scenario: keep alpha
                  Given stuff
            """,
        )
        generate_stubs("clnr", config)
        test_file = tmp_project / "tests" / "features" / "cln_rule" / "alpha_test.py"
        content = (
            test_file.read_text()
            + """
def test_unmapped():
    ...
"""
        )
        test_file.write_text(content)
        clean_unmapped("clnr", config)
        content = test_file.read_text()
        assert "test_keep_alpha" in content
        assert "test_unmapped" not in content
