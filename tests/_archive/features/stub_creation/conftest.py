"""Shared fixtures for stub-creation feature tests."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest


def _make_feature(
    features_dir: Path,
    stage: str,
    folder: str,
    filename: str,
    content: str,
) -> None:
    """Write a .feature file under features_dir/<stage>/<folder>/<filename>."""
    feature_dir = features_dir / stage / folder
    feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / filename).write_text(content, encoding="utf-8")


def _make_test_file(
    tests_dir: Path,
    feature_slug: str,
    story_slug: str,
    content: str,
) -> Path:
    """Write a test file under tests_dir/<feature_slug>/<story_slug>_test.py."""
    test_dir = tests_dir / feature_slug
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / f"{story_slug}_test.py"
    test_file.write_text(content, encoding="utf-8")
    return test_file


def _read_test_file(tests_dir: Path, feature_slug: str, story_slug: str) -> str:
    """Read test file content; returns empty string if file does not exist."""
    test_file = tests_dir / feature_slug / f"{story_slug}_test.py"
    if not test_file.exists():
        return ""
    return test_file.read_text(encoding="utf-8")


@pytest.fixture
def make_feature() -> Callable[..., None]:
    """Fixture providing the make_feature helper."""
    return _make_feature


@pytest.fixture
def make_test_file() -> Callable[..., Path]:
    """Fixture providing the make_test_file helper."""
    return _make_test_file


@pytest.fixture
def read_test_file() -> Callable[..., str]:
    """Fixture providing the read_test_file helper."""
    return _read_test_file
