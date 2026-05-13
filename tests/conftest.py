from __future__ import annotations

import os
import textwrap
from collections.abc import Generator
from pathlib import Path

import pytest

from beehave.config import Config


@pytest.fixture
def tmp_project(tmp_path: Path) -> Generator[Path]:
    features = tmp_path / "docs" / "features"
    tests = tmp_path / "tests" / "features"
    features.mkdir(parents=True)
    tests.mkdir(parents=True)
    old = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old)


@pytest.fixture
def config(tmp_project: Path) -> Config:
    return Config(
        features_dir=str(tmp_project / "docs" / "features"),
        tests_dir=str(tmp_project / "tests" / "features"),
    )


def write_feature(
    tmp_project: Path,
    name: str,
    content: str,
) -> Path:
    features_dir = tmp_project / "docs" / "features"
    parts = name.rsplit("/", 1)
    if len(parts) == 2:
        features_dir = features_dir / parts[0]
        features_dir.mkdir(parents=True, exist_ok=True)
        fname = parts[1]
    else:
        fname = parts[0]
    p = features_dir / f"{fname}.feature"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


def write_test(
    tmp_project: Path,
    feature_dir: str,
    filename: str,
    source: str,
) -> Path:
    d = tmp_project / "tests" / "features" / feature_dir
    d.mkdir(parents=True, exist_ok=True)
    p = d / filename
    p.write_text(textwrap.dedent(source), encoding="utf-8")
    return p
