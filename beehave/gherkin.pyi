# The parser + its in-memory parse model (collapsed here per Q2-resolution:
# no separate `models` shared kernel — the shapes are returned by exactly
# one public entry point, `parse_feature`, and consumed by intra-package
# collaborators in the same bounded context; tests never import them as a
# `beehave.models` module). Field shapes are binding per data-model.md §2.

class Placeholder:
    name: str

class DataTable:
    headers: list[str] | None
    rows: list[list[str]]

class Step:
    keyword: str
    text: str
    placeholders: list[Placeholder]
    docstring: str | None
    data_table: DataTable | None

class Examples:
    headers: list[str]
    rows: list[dict[str, str]]
    row_tags: list[list[str]]

class Background:
    steps: list[Step]

class Scenario:
    title: str
    slug: str
    function_name: str
    tags: list[str]
    keyword: str
    steps: list[Step]
    examples: Examples | None

class Rule:
    name: str
    tags: list[str]
    background: Background | None
    children: list[Scenario]

class Feature:
    name: str
    tags: list[str]
    background: Background | None
    children: list[Rule | Scenario]

def parse_feature(source: str) -> Feature: ...
