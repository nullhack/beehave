from __future__ import annotations

from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from beehave.config import VALID_STRATEGIES, Config, load_config


class TestConfig:
    def test_defaults(self) -> None:
        c = Config()
        assert c.features_dir == "docs/features"
        assert c.tests_dir == "tests/features"
        assert c.default_strategy == "text"
        assert c.background_check_numeric is True
        assert c.background_check_string is True

    def test_invalid_strategy_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid default_strategy"):
            Config(default_strategy="bad")

    def test_strategy_expr(self) -> None:
        assert Config(default_strategy="text").default_strategy_expr == "st.text()"
        assert (
            Config(default_strategy="integers").default_strategy_expr == "st.integers()"
        )
        assert Config(default_strategy="floats").default_strategy_expr == "st.floats()"
        assert (
            Config(default_strategy="booleans").default_strategy_expr == "st.booleans()"
        )

    @given(st.sampled_from(list(VALID_STRATEGIES)))
    @settings(max_examples=10)
    def test_all_valid_strategies_accepted(self, strategy: str) -> None:
        c = Config(default_strategy=strategy)
        assert c.default_strategy == strategy

    def test_load_config_no_pyproject(self, tmp_path: Path) -> None:
        c = load_config(tmp_path)
        assert c.features_dir == "docs/features"

    def test_load_config_with_pyproject(self, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.beehave]\nfeatures_dir = "custom/features"\n'
            'tests_dir = "custom/tests"\n'
            'default_strategy = "integers"\n'
            "background_check_numeric = false\n",
            encoding="utf-8",
        )
        c = load_config(tmp_path)
        assert c.features_dir == "custom/features"
        assert c.tests_dir == "custom/tests"
        assert c.default_strategy == "integers"
        assert c.background_check_numeric is False

    def test_load_config_partial_override(self, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.beehave]\nfeatures_dir = "my/features"\n',
            encoding="utf-8",
        )
        c = load_config(tmp_path)
        assert c.features_dir == "my/features"
        assert c.tests_dir == "tests/features"
        assert c.background_check_numeric is True
