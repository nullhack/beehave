"""Shared value objects for pytest-beehave."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FeatureStage(Enum):
    """The lifecycle stage of a feature folder."""

    BACKLOG = "backlog"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class ExampleId:
    """An 8-char hex identifier for a Gherkin Example.

    Attributes:
        value: The 8-character lowercase hexadecimal string.
    """

    value: str

    def __str__(self) -> str:
        """Return the hex string representation."""
        return self.value


@dataclass(frozen=True, slots=True)
class FeatureSlug:
    """A Python-safe slug derived from a feature folder name.

    Attributes:
        value: Lowercase, underscore-separated identifier.
    """

    value: str

    def __str__(self) -> str:
        """Return the slug string."""
        return self.value

    @classmethod
    def from_folder_name(cls, name: str) -> "FeatureSlug":
        """Create a FeatureSlug from a kebab-case folder name.

        Args:
            name: The feature folder name (may contain hyphens).

        Returns:
            A FeatureSlug with hyphens replaced by underscores.
        """
        return cls(name.replace("-", "_").lower())


@dataclass(frozen=True, slots=True)
class RuleSlug:
    """A file-safe slug derived from a Rule block title.

    Attributes:
        value: Lowercase, hyphen-separated identifier.
    """

    value: str

    def __str__(self) -> str:
        """Return the slug string."""
        return self.value

    @classmethod
    def from_rule_title(cls, title: str) -> "RuleSlug":
        """Create a RuleSlug from a Rule block title.

        Args:
            title: The Rule: title text.

        Returns:
            A RuleSlug with spaces and hyphens replaced by underscores, lowercased.
        """
        return cls(title.strip().replace("-", "_").replace(" ", "_").lower())
