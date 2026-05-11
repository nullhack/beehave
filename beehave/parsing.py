from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    name: str


@dataclass(frozen=True)
class TestModule:
    path: Path


@dataclass(frozen=True)
class TestDirectory:
    path: Path


@dataclass
class FeatureFile:
    name: str
    rules: list[Rule] = field(default_factory=list)

    @property
    def stem(self) -> str:
        raise NotImplementedError


def resolve_test_module_path(feature_name: str, rule: Rule | None) -> TestModule:
    raise NotImplementedError


def resolve_all_test_modules(feature_file: FeatureFile) -> list[TestModule]:
    raise NotImplementedError


def resolve_test_directory(feature_name: str) -> TestDirectory:
    raise NotImplementedError
