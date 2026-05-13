from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

VALID_STRATEGIES = ("text", "integers", "floats", "booleans")

_STRATEGY_MAP = {
    "text": "st.text()",
    "integers": "st.integers()",
    "floats": "st.floats()",
    "booleans": "st.booleans()",
}


@dataclass(frozen=True)
class Config:
    features_dir: str = "docs/features"
    tests_dir: str = "tests/features"
    default_strategy: str = "text"
    max_examples: int = 1
    background_check_numeric: bool = True
    background_check_string: bool = True

    def __post_init__(self) -> None:
        if self.default_strategy not in VALID_STRATEGIES:
            raise ValueError(
                f"Invalid default_strategy '{self.default_strategy}'. "
                f"Valid options: {', '.join(VALID_STRATEGIES)}"
            )

    @property
    def default_strategy_expr(self) -> str:
        return _STRATEGY_MAP[self.default_strategy]


def load_config(project_root: Path | None = None) -> Config:
    root = project_root or Path.cwd()
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return Config()
    with open(pyproject, "rb") as f:
        data = tomllib.load(f)
    tool = data.get("tool", {}).get("beehave", {})
    return Config(
        features_dir=tool.get("features_dir", "docs/features"),
        tests_dir=tool.get("tests_dir", "tests/features"),
        default_strategy=tool.get("default_strategy", "text"),
        max_examples=tool.get("max_examples", 1),
        background_check_numeric=tool.get("background_check_numeric", True),
        background_check_string=tool.get("background_check_string", True),
    )
