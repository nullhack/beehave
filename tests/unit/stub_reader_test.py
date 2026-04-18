"""Unit tests for pytest_beehave.stub_reader module."""

from pathlib import Path

from pytest_beehave.models import ExampleId
from pytest_beehave.stub_reader import (
    _extract_docstring,
    _find_triple_quote_end,
    extract_example_id_from_name,
    read_stubs_from_file,
)


def test_extract_example_id_from_name_returns_id_when_matched() -> None:
    """
    Given: A function name with an 8-char hex suffix
    When: extract_example_id_from_name is called
    Then: Returns the ExampleId
    """
    result = extract_example_id_from_name("test_my_feature_aabbccdd")
    assert result == ExampleId("aabbccdd")


def test_extract_example_id_from_name_returns_none_when_no_match() -> None:
    """
    Given: A string without an 8-char hex suffix
    When: extract_example_id_from_name is called
    Then: Returns None
    """
    result = extract_example_id_from_name("not_a_test_function")
    assert result is None


def test_find_triple_quote_end_returns_content_length_when_unclosed() -> None:
    """
    Given: Content where the triple-quote is never closed
    When: _find_triple_quote_end is called
    Then: Returns the length of the content
    """
    content = '"""unclosed string without end'
    result = _find_triple_quote_end(content, 0, '"""')
    assert result == len(content)


def test_extract_docstring_returns_empty_when_no_newline_after_def() -> None:
    """
    Given: Content where there is no newline after the def line position
    When: _extract_docstring is called with func_start at the last line
    Then: Returns empty string
    """
    content = "def test_foo_aabbccdd() -> None:"
    # func_start at 0, no newline in content → def_end == -1
    result = _extract_docstring(content, 0)
    assert result == ""


def test_extract_docstring_returns_empty_when_no_triple_quote() -> None:
    """
    Given: A function with no docstring after the def line
    When: _extract_docstring is called
    Then: Returns empty string
    """
    content = "def test_foo_aabbccdd() -> None:\n    pass\n"
    result = _extract_docstring(content, 0)
    assert result == ""


def test_extract_docstring_returns_empty_when_unclosed_triple_quote() -> None:
    """
    Given: A function with an unclosed triple-quote docstring
    When: _extract_docstring is called
    Then: Returns empty string
    """
    content = 'def test_foo_aabbccdd() -> None:\n    """unclosed docstring without end'
    result = _extract_docstring(content, 0)
    assert result == ""


def test_read_stubs_from_file_returns_empty_when_file_not_exists(
    tmp_path: Path,
) -> None:
    """
    Given: A path to a file that does not exist
    When: read_stubs_from_file is called
    Then: Returns an empty list
    """
    missing = tmp_path / "no_such_file_test.py"
    result = read_stubs_from_file(missing)
    assert result == []


def test_read_stubs_from_file_skips_function_inside_string(tmp_path: Path) -> None:
    """
    Given: A test file with a def statement inside a triple-quoted string
    When: read_stubs_from_file is called
    Then: The embedded function is not returned as a stub
    """
    test_file = tmp_path / "example_test.py"
    test_file.write_text(
        '"""Tests.\n'
        "def test_feature_aabbccdd() -> None:\n"
        '    pass\n"""\n'
        "\nimport pytest\n",
        encoding="utf-8",
    )
    result = read_stubs_from_file(test_file)
    assert result == []


def test_read_stubs_from_file_reads_real_stubs(tmp_path: Path) -> None:
    """
    Given: A test file with a real test function
    When: read_stubs_from_file is called
    Then: Returns ExistingStub with correct data
    """
    test_file = tmp_path / "examples_test.py"
    test_file.write_text(
        '"""Tests for examples story."""\n\n'
        "import pytest\n\n\n"
        '@pytest.mark.skip(reason="not yet implemented")\n'
        "def test_my_feature_aabbccdd() -> None:\n"
        '    """\n'
        "    Given: Something\n"
        "    When: Something happens\n"
        "    Then: Result\n"
        '    """\n'
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )
    result = read_stubs_from_file(test_file)
    assert len(result) == 1
    stub = result[0]
    assert stub.function_name == "test_my_feature_aabbccdd"
    assert stub.example_id == ExampleId("aabbccdd")
    assert "pytest.mark.skip(reason=" in " ".join(stub.markers)


def test_read_stubs_from_file_reads_class_method_stubs(tmp_path: Path) -> None:
    """
    Given: A test file with a class-method stub inside a Test class
    When: read_stubs_from_file is called
    Then: Returns ExistingStub with correct class_name
    """
    test_file = tmp_path / "my_rule_test.py"
    test_file.write_text(
        '"""Tests for my_rule story."""\n\n'
        "import pytest\n\n\n"
        "class TestMyRule:\n"
        '    @pytest.mark.skip(reason="not yet implemented")\n'
        "    def test_my_feature_aabbccdd(self) -> None:\n"
        '        """\n'
        "        Given: Something\n"
        "        When: Something happens\n"
        "        Then: Result\n"
        '        """\n'
        "        raise NotImplementedError\n",
        encoding="utf-8",
    )
    result = read_stubs_from_file(test_file)
    assert len(result) == 1
    stub = result[0]
    assert stub.function_name == "test_my_feature_aabbccdd"
    assert stub.class_name == "TestMyRule"


def test_read_stubs_from_file_indented_without_class_returns_none_class(
    tmp_path: Path,
) -> None:
    """
    Given: A test file where a def line is indented but has no class before it
    When: read_stubs_from_file is called
    Then: Returns ExistingStub with class_name=None
    """
    test_file = tmp_path / "edge_case_test.py"
    # Indented function with no class declaration above it
    test_file.write_text(
        "if True:\n"
        "    def test_my_feature_aabbccdd() -> None:\n"
        '        """Given: x\nWhen: y\nThen: z\n"""\n'
        "        pass\n",
        encoding="utf-8",
    )
    result = read_stubs_from_file(test_file)
    assert len(result) == 1
    assert result[0].class_name is None
