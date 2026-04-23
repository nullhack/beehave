"""Entry point for running the application as a module."""

from __future__ import annotations

import logging
from pathlib import Path

import fire

from pytest_beehave.nest import NestConfig, nest

logger = logging.getLogger(__name__)


def main(verbosity: str = "INFO") -> None:
    """Run the application.

    Args:
        verbosity: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    logging.basicConfig(
        level=getattr(logging, verbosity.upper(), logging.INFO),
        format="%(levelname)s - %(name)s: %(message)s",
    )
    logger.info("Ready.")


class BeehaveCLI:
    """Command-line interface for beehave."""

    def main(self, verbosity: str = "INFO") -> None: ...

    def nest(
        self,
        features_dir: str = "",
        check: bool = False,
        overwrite: bool = False,
    ) -> None: ...


if __name__ == "__main__":
    fire.Fire(BeehaveCLI)
