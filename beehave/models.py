from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Placeholder:
    name: str


@dataclass(frozen=True)
class Literal:
    value: str | int | float | bool
    raw: str


@dataclass(frozen=True)
class ParsedStep:
    keyword: str
    text: str
    placeholders: tuple[Placeholder, ...] = ()
    literals: tuple[Literal, ...] = ()
    line: int = 0


@dataclass(frozen=True)
class ExamplesTable:
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class ScenarioInfo:
    title: str
    function_name: str
    steps: tuple[ParsedStep, ...]
    placeholders: tuple[Placeholder, ...]
    literals: tuple[Literal, ...]
    examples: ExamplesTable | None
    is_outline: bool
    feature_title: str
    feature_path: str
    line: int = 0


@dataclass(frozen=True)
class TestInfo:
    function_name: str
    given_kwargs: tuple[str, ...] = ()
    example_rows: tuple[dict[str, object], ...] = ()
    body_name_nodes: tuple[str, ...] = ()
    body_constant_nodes: tuple[object, ...] = ()
    is_stub: bool = False
    line: int = 0


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    error_type: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.error_type}: {self.message}"
