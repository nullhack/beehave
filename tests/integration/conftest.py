from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "pending: v2 source not yet built; skipped until the build subflow removes the marker",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    skip = pytest.mark.skip(reason="pending v2 source")
    for item in items:
        if "pending" in item.keywords:
            item.add_marker(skip)
