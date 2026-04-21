"""Hatch command — generate bee-themed example features directory."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from pathlib import Path

_FEATURE_NAMES = [
    "The Forager's Journey",
    "Queen's Decree",
    "Drone Assembly Protocol",
    "Worker Bee Orientation",
    "Nectar Collection Workflow",
    "Hive Temperature Regulation",
    "Pollen Scout Dispatch",
    "Royal Jelly Production",
    "Swarm Formation Ritual",
    "Honeycomb Architecture Review",
]

_BEES = [
    "Beatrice",
    "Boris",
    "Belinda",
    "Bruno",
    "Blossom",
    "Barnaby",
    "Bridget",
    "Bertram",
]
_HIVES = ["the Golden Hive", "the Amber Hive", "the Crystal Hive", "the Obsidian Hive"]

_BACKLOG_CONTENT = """\
Feature: {feature_name}

  As {bee}, a worker bee in {hive}
  I want to complete my assigned foraging route
  So that the colony has enough nectar for the season

  Rule: Forager readiness

    @id:hatch001
    Example: Forager departs when pollen reserve is below threshold
      Given the pollen reserve is below 30 percent
      When the forager sensor detects the shortage
      Then {bee} departs for the meadow within one waggle cycle

    Example: Untagged scenario triggers auto-ID assignment
      Given the hive registers a new forager
      When the forager completes orientation
      Then the forager is assigned a unique scout ID

    @deprecated
    Example: Legacy hive-entry handshake (deprecated)
      Given an older forager approaches the hive entrance
      When the guard bee checks the legacy handshake
      Then the handshake is accepted but logged as deprecated

  Rule: Nectar quality control

    @id:hatch002
    Example: Low-quality nectar is rejected at the gate
      Given a forager returns with nectar of quality below 0.4 brix
      When the gate inspector evaluates the sample
      Then the nectar is rejected and the forager is sent to a higher-quality source
"""

_IN_PROGRESS_CONTENT = """\
# language: en
Feature: Waggle Dance Communication

  Background:
    Given the hive is in active foraging mode
    And the dance floor is clear of obstacles

  Rule: Direction encoding

    @id:hatch003
    Example: Scout encodes flower direction in waggle run angle
      Given a scout has located flowers 200 metres to the north-east
      When the scout performs the waggle dance
      Then the waggle run angle matches the sun-relative bearing to the flowers

  Rule: Distance encoding

    @id:hatch004
    Scenario Outline: Scout encodes distance via waggle run duration
      Given a scout has located flowers at <distance> metres
      When the scout performs the waggle dance
      Then the waggle run lasts approximately <duration> milliseconds

      Examples:
        | distance | duration |
        | 100      | 250      |
        | 500      | 875      |
        | 1000     | 1500     |

    @id:hatch005
    Example: Scout provides a data table of visited flower patches
      Given the scout returns from a multi-patch forage
      When the scout performs the waggle dance
      Then the flower patch register contains the following entries:
        | patch_id | species       | quality |
        | P-001    | Lavender      | 0.92    |
        | P-002    | Clover        | 0.85    |
        | P-003    | Sunflower     | 0.78    |
"""

_COMPLETED_CONTENT = """\
Feature: Colony Winter Preparation

  As {bee}, the winter logistics coordinator in {hive}
  I want to ensure honey stores are sufficient before the first frost
  So that the colony survives the winter without starvation

  Rule: Honey reserve verification

    @id:hatch006
    Example: Winter preparation passes when honey reserve exceeds minimum
      Given the honey reserve is at 85 percent capacity
      When the winter readiness check is performed
      Then the colony status is set to WINTER-READY

    @id:hatch007
    Example: Winter preparation fails when honey reserve is insufficient
      Given the honey reserve is below 60 percent capacity
      When the winter readiness check is performed
      Then the colony status is set to AT-RISK and an alert is raised for {bee}
"""


@dataclass(frozen=True, slots=True)
class HatchFile:
    """A single generated .feature file to be written.

    Attributes:
        relative_path: Path relative to the features root (e.g. ``backlog/x.feature``).
        content: The full Gherkin text to write.
    """

    relative_path: str
    content: str


def generate_hatch_files() -> list[HatchFile]:
    """Generate bee-themed example .feature files using stdlib randomisation.

    Returns:
        A list of HatchFile objects ready to be written to disk.
    """
    feature_name = secrets.choice(_FEATURE_NAMES)
    bee = secrets.choice(_BEES)
    hive = secrets.choice(_HIVES)

    return [
        HatchFile(
            relative_path="backlog/forager-journey.feature",
            content=_BACKLOG_CONTENT.format(
                feature_name=feature_name, bee=bee, hive=hive
            ),
        ),
        HatchFile(
            relative_path="in-progress/waggle-dance.feature",
            content=_IN_PROGRESS_CONTENT,
        ),
        HatchFile(
            relative_path="completed/winter-preparation.feature",
            content=_COMPLETED_CONTENT.format(bee=bee, hive=hive),
        ),
    ]


def write_hatch(features_root: Path, files: list[HatchFile]) -> list[str]:
    """Write HatchFile objects to disk under features_root.

    Args:
        features_root: The root features directory to write into.
        files: The list of HatchFile objects to write.

    Returns:
        List of written file paths as strings (relative to features_root).
    """
    written: list[str] = []
    for hatch_file in files:
        dest = features_root / hatch_file.relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(hatch_file.content, encoding="utf-8")
        written.append(hatch_file.relative_path)
    return written


def run_hatch(features_root: Path, force: bool) -> list[str]:
    """Run the hatch command: check for conflicts, generate, and write files.

    Args:
        features_root: The root features directory to populate.
        force: If True, overwrite existing content without error.

    Returns:
        List of written file paths as strings.

    Raises:
        SystemExit: If the directory contains .feature files and force is False.
    """
    existing = list(features_root.rglob("*.feature")) if features_root.exists() else []
    if existing and not force:
        conflict = existing[0]
        raise SystemExit(
            f"[beehave] hatch aborted: existing .feature files found at {conflict}. "
            "Use --beehave-hatch-force to overwrite."
        )
    for old_file in existing:
        old_file.unlink()
    return write_hatch(features_root, generate_hatch_files())
