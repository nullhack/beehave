"""Sync engine for pytest-beehave — orchestrates stub creation and updates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pytest_beehave.feature_parser import (
    ParsedExample,
    ParsedFeature,
    ParsedRule,
    parse_feature,
)
from pytest_beehave.models import ExampleId, FeatureStage
from pytest_beehave.stub_reader import ExistingStub, read_stubs_from_file
from pytest_beehave.stub_writer import (
    StubSpec,
    SyncAction,
    build_class_name,
    build_docstring,
    build_function_name,
    mark_non_conforming,
    mark_orphan,
    remove_orphan_marker,
    toggle_deprecated_marker,
    update_docstring,
    write_stub_to_file,
)

_FEATURE_STAGES = (
    FeatureStage.BACKLOG,
    FeatureStage.IN_PROGRESS,
    FeatureStage.COMPLETED,
)


class FileSystemProtocol(Protocol):
    """Protocol for filesystem operations needed by the sync engine."""

    def list_feature_files(self, stage_dir: Path) -> list[Path]:  # pragma: no cover
        """List all .feature files recursively under stage_dir."""
        ...

    def list_test_files(self, tests_dir: Path) -> list[Path]:  # pragma: no cover
        """List all *_test.py files recursively under tests_dir."""
        ...


@dataclass(frozen=True, slots=True)
class _RealFileSystem:
    """Concrete filesystem adapter using pathlib."""

    def list_feature_files(self, stage_dir: Path) -> list[Path]:
        """List all .feature files recursively under stage_dir.

        Args:
            stage_dir: Root directory to search.

        Returns:
            Sorted list of .feature file paths.
        """
        return sorted(stage_dir.rglob("*.feature"))

    def list_test_files(self, tests_dir: Path) -> list[Path]:
        """List all *_test.py files recursively under tests_dir.

        Args:
            tests_dir: Root directory to search.

        Returns:
            Sorted list of test file paths.
        """
        return sorted(tests_dir.rglob("*_test.py"))


@dataclass(frozen=True, slots=True)
class SyncResult:
    """Result of a sync operation.

    Attributes:
        actions: Tuple of SyncAction objects describing what was done.
    """

    actions: tuple[SyncAction, ...]

    @property
    def is_noop(self) -> bool:
        """Return True if no actions were taken."""
        return len(self.actions) == 0


def _collect_all_ids(
    features_dir: Path,
    filesystem: FileSystemProtocol,
) -> frozenset[ExampleId]:
    """Collect all example IDs from all .feature files.

    Args:
        features_dir: Root of the features directory.
        filesystem: Filesystem adapter.

    Returns:
        Frozenset of ExampleId objects.
    """
    import re

    id_re = re.compile(r"@id:([a-f0-9]{8})")
    ids: set[ExampleId] = set()
    for stage in _FEATURE_STAGES:
        stage_dir = features_dir / stage.value
        if not stage_dir.exists():
            continue
        for path in filesystem.list_feature_files(stage_dir):
            text = path.read_text(encoding="utf-8")
            ids.update(ExampleId(match.group(1)) for match in id_re.finditer(text))
    return frozenset(ids)


def _add_rule_locations(
    feature_dir: Path,
    feature: ParsedFeature,
    locations: dict[ExampleId, tuple[Path, str | None]],
) -> None:
    """Add expected locations for all rule-based examples of a feature.

    Args:
        feature_dir: The test directory for this feature.
        feature: The parsed feature.
        locations: Dict to populate with ExampleId -> (file, class) entries.
    """
    for rule in feature.rules:
        test_file = feature_dir / f"{rule.rule_slug}_test.py"
        class_name = build_class_name(rule.rule_slug)
        for example in rule.examples:
            locations[example.example_id] = (test_file, class_name)


def _build_expected_locations(
    feature_stage_pairs: list[tuple[ParsedFeature, FeatureStage]],
    tests_dir: Path,
) -> dict[ExampleId, tuple[Path, str | None]]:
    """Build a map of ExampleId to (expected_test_file, expected_class_name).

    Args:
        feature_stage_pairs: All parsed feature/stage tuples.
        tests_dir: Root of the tests/features/ directory.

    Returns:
        Dict mapping ExampleId to (file_path, class_name_or_None).
    """
    locations: dict[ExampleId, tuple[Path, str | None]] = {}
    for feature, _stage in feature_stage_pairs:
        feature_dir = tests_dir / str(feature.feature_slug)
        _add_rule_locations(feature_dir, feature, locations)
        top_level_file = feature_dir / "examples_test.py"
        for example in feature.top_level_examples:
            locations[example.example_id] = (top_level_file, None)
    return locations


def _orphan_action(
    test_file: Path,
    stub: ExistingStub,
    all_ids: frozenset[ExampleId],
) -> SyncAction | None:
    """Compute the orphan sync action for a single stub.

    Args:
        test_file: The test file containing the stub.
        stub: The existing stub.
        all_ids: All known example IDs.

    Returns:
        SyncAction or None.
    """
    if stub.example_id not in all_ids:
        return mark_orphan(test_file, stub.function_name)
    return remove_orphan_marker(test_file, stub.function_name)


def _orphan_actions_for_file(
    test_file: Path,
    all_ids: frozenset[ExampleId],
) -> list[SyncAction]:
    """Compute orphan sync actions for all stubs in a single test file.

    Args:
        test_file: The test file to scan.
        all_ids: All known example IDs.

    Returns:
        List of SyncAction objects.
    """
    return [
        action
        for stub in read_stubs_from_file(test_file)
        for action in [_orphan_action(test_file, stub, all_ids)]
        if action is not None
    ]


def _sync_orphans(
    tests_dir: Path,
    all_ids: frozenset[ExampleId],
    filesystem: FileSystemProtocol,
) -> list[SyncAction]:
    """Add or remove orphan markers for test functions without matching @id.

    Args:
        tests_dir: Root of the tests/features/ directory.
        all_ids: All known example IDs.
        filesystem: Filesystem adapter.

    Returns:
        List of SyncAction objects.
    """
    actions: list[SyncAction] = []
    for test_file in filesystem.list_test_files(tests_dir):
        actions.extend(_orphan_actions_for_file(test_file, all_ids))
    return actions


def _check_stub_conformity(
    test_file: Path,
    stub: ExistingStub,
    expected_locations: dict[ExampleId, tuple[Path, str | None]],
) -> SyncAction | None:
    """Check if a single stub is in the correct file and mark it if not.

    Args:
        test_file: The file the stub was found in.
        stub: The existing stub.
        expected_locations: Map of ExampleId to (expected_file, expected_class).

    Returns:
        SyncAction if non-conforming, else None.
    """
    if stub.example_id not in expected_locations:
        return None
    expected_file, expected_class = expected_locations[stub.example_id]
    if expected_class is None or test_file == expected_file:
        return None
    return mark_non_conforming(
        test_file, stub.function_name, expected_file, expected_class
    )


def _non_conforming_actions_for_file(
    test_file: Path,
    expected_locations: dict[ExampleId, tuple[Path, str | None]],
) -> list[SyncAction]:
    """Collect non-conforming actions for all stubs in one test file.

    Args:
        test_file: Path to the test file.
        expected_locations: Map of ExampleId to (expected_file, expected_class).

    Returns:
        List of SyncAction objects for non-conforming stubs.
    """
    return [
        action
        for stub in read_stubs_from_file(test_file)
        for action in [_check_stub_conformity(test_file, stub, expected_locations)]
        if action is not None
    ]


def _sync_non_conforming(
    tests_dir: Path,
    expected_locations: dict[ExampleId, tuple[Path, str | None]],
    filesystem: FileSystemProtocol,
) -> list[SyncAction]:
    """Mark test stubs found in the wrong file as non-conforming.

    Only applies to Rule-based stubs (those with an expected class). Top-level
    examples without a class context are skipped — orphan detection handles
    unrecognised test files.

    Args:
        tests_dir: Root of the tests/features/ directory.
        expected_locations: Map of ExampleId to (expected_file, expected_class).
        filesystem: Filesystem adapter.

    Returns:
        List of SyncAction objects.
    """
    actions: list[SyncAction] = []
    for test_file in filesystem.list_test_files(tests_dir):
        actions.extend(_non_conforming_actions_for_file(test_file, expected_locations))
    return actions


def _sync_active_feature(
    feature: ParsedFeature,
    tests_dir: Path,
) -> list[SyncAction]:
    """Sync stubs for an active (backlog/in-progress) feature.

    Args:
        feature: The parsed feature.
        tests_dir: Root of the tests/features/ directory.

    Returns:
        List of SyncAction objects.
    """
    actions: list[SyncAction] = []
    feature_test_dir = tests_dir / str(feature.feature_slug)

    if feature.rules:
        for rule in feature.rules:
            actions.extend(_sync_rule_stubs(feature, rule, feature_test_dir))
    elif feature.top_level_examples:
        actions.extend(_sync_top_level_stubs(feature, feature_test_dir))

    return actions


def _sync_rule_stubs(
    feature: ParsedFeature,
    rule: ParsedRule,
    feature_test_dir: Path,
) -> list[SyncAction]:
    """Sync stubs for a single rule block.

    Args:
        feature: The parsed feature.
        rule: The parsed rule.
        feature_test_dir: Directory for this feature's tests.

    Returns:
        List of SyncAction objects.
    """
    if not rule.examples:
        return []
    test_file = feature_test_dir / f"{rule.rule_slug}_test.py"
    existing = {s.example_id: s for s in read_stubs_from_file(test_file)}
    actions: list[SyncAction] = []
    for example in rule.examples:
        action = _sync_one_example(feature, rule, example, test_file, existing)
        if action is not None:
            actions.append(action)
    actions.extend(_sync_deprecated_in_rule(feature, rule, test_file))
    return actions


def _update_existing_stub(
    feature: ParsedFeature,
    rule: ParsedRule | None,
    example: ParsedExample,
    test_file: Path,
    stub: ExistingStub,
) -> SyncAction | None:
    """Update an existing stub's docstring and/or name.

    Args:
        feature: The parsed feature.
        rule: The parsed rule (or None for top-level).
        example: The parsed example.
        test_file: Path to the test file.
        stub: The existing stub to update.

    Returns:
        SyncAction or None.
    """
    return update_docstring(
        test_file,
        stub.function_name,
        build_docstring(feature, rule, example),
        feature.feature_slug,
        example.example_id,
    )


def _sync_one_example(
    feature: ParsedFeature,
    rule: ParsedRule | None,
    example: ParsedExample,
    test_file: Path,
    existing: dict[ExampleId, ExistingStub],
) -> SyncAction | None:
    """Sync a single example stub — create or update.

    Args:
        feature: The parsed feature.
        rule: The parsed rule (or None for top-level).
        example: The parsed example.
        test_file: Path to the test file.
        existing: Map of existing stubs by example ID.

    Returns:
        SyncAction or None.
    """
    if example.example_id in existing:
        return _update_existing_stub(
            feature, rule, example, test_file, existing[example.example_id]
        )
    rule_slug = rule.rule_slug if rule else None
    spec = StubSpec(
        feature_slug=feature.feature_slug,
        rule_slug=rule_slug,
        example=example,
        feature=feature,
    )
    return write_stub_to_file(test_file, spec)


def _sync_deprecated_in_rule(
    feature: ParsedFeature,
    rule: ParsedRule,
    test_file: Path,
) -> list[SyncAction]:
    """Sync deprecated markers for all examples in a rule.

    Args:
        feature: The parsed feature.
        rule: The parsed rule.
        test_file: Path to the test file.

    Returns:
        List of SyncAction objects.
    """
    return [
        action
        for example in rule.examples
        for action in [
            toggle_deprecated_marker(
                test_file,
                build_function_name(feature.feature_slug, example.example_id),
                should_be_deprecated=example.is_deprecated,
            )
        ]
        if action is not None
    ]


def _sync_top_level_stubs(
    feature: ParsedFeature,
    feature_test_dir: Path,
) -> list[SyncAction]:
    """Sync stubs for top-level examples (no Rule blocks).

    Args:
        feature: The parsed feature.
        feature_test_dir: Directory for this feature's tests.

    Returns:
        List of SyncAction objects.
    """
    test_file = feature_test_dir / "examples_test.py"
    existing = {s.example_id: s for s in read_stubs_from_file(test_file)}
    actions: list[SyncAction] = []
    for example in feature.top_level_examples:
        action = _sync_one_example(feature, None, example, test_file, existing)
        if action is not None:
            actions.append(action)
    actions.extend(_sync_deprecated_top_level(feature, test_file))
    return actions


def _sync_deprecated_top_level(
    feature: ParsedFeature,
    test_file: Path,
) -> list[SyncAction]:
    """Sync deprecated markers for top-level examples (no Rule blocks).

    Args:
        feature: The parsed feature.
        test_file: Path to the top-level examples test file.

    Returns:
        List of SyncAction objects.
    """
    return [
        action
        for example in feature.top_level_examples
        for action in [
            toggle_deprecated_marker(
                test_file,
                build_function_name(feature.feature_slug, example.example_id),
                should_be_deprecated=example.is_deprecated,
            )
        ]
        if action is not None
    ]


def _sync_deprecated_rules(
    feature: ParsedFeature,
    feature_test_dir: Path,
) -> list[SyncAction]:
    """Sync deprecated markers for all rules in a feature.

    Args:
        feature: The parsed feature.
        feature_test_dir: Directory for this feature's tests.

    Returns:
        List of SyncAction objects.
    """
    actions: list[SyncAction] = []
    for rule in feature.rules:
        test_file = feature_test_dir / f"{rule.rule_slug}_test.py"
        actions.extend(_sync_deprecated_in_rule(feature, rule, test_file))
    return actions


def _sync_completed_feature(
    feature: ParsedFeature,
    tests_dir: Path,
) -> list[SyncAction]:
    """Sync deprecated markers only for a completed feature.

    Args:
        feature: The parsed feature.
        tests_dir: Root of the tests/features/ directory.

    Returns:
        List of SyncAction objects.
    """
    feature_test_dir = tests_dir / str(feature.feature_slug)
    if feature.rules:
        return _sync_deprecated_rules(feature, feature_test_dir)
    return _sync_deprecated_top_level(feature, feature_test_dir / "examples_test.py")


def _folder_name_for(feature_path: Path, stage_dir: Path) -> str:
    """Derive the folder name for a feature file.

    Args:
        feature_path: Path to the .feature file.
        stage_dir: The stage directory (backlog/, in-progress/, completed/).

    Returns:
        Folder name string used as the feature slug source.
    """
    feature_parent = feature_path.parent
    if feature_parent == stage_dir:
        return feature_path.stem
    return feature_parent.name


def _features_in_stage(
    stage: FeatureStage,
    features_dir: Path,
    filesystem: FileSystemProtocol,
) -> list[tuple[ParsedFeature, FeatureStage]]:
    """Discover all feature files for one stage directory.

    Args:
        stage: The feature stage.
        features_dir: Root of the features directory.
        filesystem: Filesystem adapter.

    Returns:
        List of (ParsedFeature, FeatureStage) tuples for this stage.
    """
    stage_dir = features_dir / stage.value
    if not stage_dir.exists():
        return []
    return [
        (parse_feature(p, _folder_name_for(p, stage_dir)), stage)
        for p in filesystem.list_feature_files(stage_dir)
    ]


def discover_feature_locations(
    features_dir: Path,
    filesystem: FileSystemProtocol,
) -> list[tuple[ParsedFeature, FeatureStage]]:
    """Discover all feature files and their stages.

    Args:
        features_dir: Root of the features directory.
        filesystem: Filesystem adapter.

    Returns:
        List of (ParsedFeature, FeatureStage) tuples.
    """
    results: list[tuple[ParsedFeature, FeatureStage]] = []
    for stage in _FEATURE_STAGES:
        results.extend(_features_in_stage(stage, features_dir, filesystem))
    return results


def run_sync(
    features_root: Path,
    tests_root: Path,
    filesystem: FileSystemProtocol | None = None,
) -> list[str]:
    """Sync test stubs from .feature files to the tests directory.

    Args:
        features_root: Root of the features directory (contains backlog/,
            in-progress/, completed/).
        tests_root: Root of the tests/features/ directory.
        filesystem: Optional filesystem adapter. Defaults to _RealFileSystem.

    Returns:
        List of action description strings.
    """
    if filesystem is None:
        filesystem = _RealFileSystem()
    actions: list[SyncAction] = []
    feature_stage_pairs = discover_feature_locations(features_root, filesystem)
    for feature, stage in feature_stage_pairs:
        if stage == FeatureStage.COMPLETED:
            actions.extend(_sync_completed_feature(feature, tests_root))
        else:
            actions.extend(_sync_active_feature(feature, tests_root))
    expected_locations = _build_expected_locations(feature_stage_pairs, tests_root)
    actions.extend(_sync_non_conforming(tests_root, expected_locations, filesystem))
    all_ids = _collect_all_ids(features_root, filesystem)
    actions.extend(_sync_orphans(tests_root, all_ids, filesystem))
    return [str(a) for a in actions]
