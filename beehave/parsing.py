from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    """A Gherkin Rule block within a feature file.

    Attributes:
        name: The human-readable name of the Rule, normalized to snake_case
            for test module naming.
    """

    name: str


@dataclass(frozen=True)
class TestModule:
    """A test file produced by mapping a FeatureFile and Rule.

    Attributes:
        path: The resolved file path, e.g.
            tests/features/<feature_stem>/<rule_name>_test.py.
    """

    __test__ = False
    path: Path


@dataclass(frozen=True)
class TestDirectory:
    """A directory under tests/features/ that contains test modules.

    Attributes:
        path: The directory path, e.g. tests/features/<feature_stem>/.
    """

    path: Path


@dataclass
class FeatureFile:
    """A parsed .feature file containing Gherkin Rules.

    Attributes:
        name: The filename of the .feature file.
        rules: The list of Gherkin Rule blocks defined in the file.
    """

    name: str
    rules: list[Rule] = field(default_factory=list)

    @property
    def stem(self) -> str:
        """The filename stem without the .feature extension."""
        raise NotImplementedError


def _normalize_to_snake_case(name: str) -> str:
    """Convert a human-readable name to snake_case for file naming.

    Args:
        name: The human-readable name to normalize.

    Returns:
        The name in lowercase with spaces replaced by underscores.
    """
    return name.lower().replace(" ", "_")


def resolve_test_module_path(feature_name: str, rule: Rule | None) -> TestModule:
    """Resolve the test module path for a feature file and optional Rule.

    Args:
        feature_name: The .feature filename.
        rule: The Gherkin Rule, or None for features without Rules.

    Returns:
        A TestModule with the resolved file path.
    """
    stem = Path(feature_name).stem
    module_name = _normalize_to_snake_case(rule.name) if rule is not None else "default"
    return TestModule(path=Path(f"tests/features/{stem}/{module_name}_test.py"))


def resolve_all_test_modules(
    feature_file: FeatureFile,
) -> list[TestModule]:
    """Resolve all test module paths for a feature file.

    If the feature has no Rules, returns a single default module.
    Otherwise, returns one module per Rule.

    Args:
        feature_file: The parsed feature file.

    Returns:
        A list of TestModules, one per Rule or a single default.
    """
    if not feature_file.rules:
        return [resolve_test_module_path(feature_file.name, None)]
    return [
        resolve_test_module_path(feature_file.name, rule) for rule in feature_file.rules
    ]


def resolve_test_directory(feature_name: str) -> TestDirectory:
    """Resolve the test directory path for a feature file.

    Args:
        feature_name: The .feature filename.

    Returns:
        A TestDirectory with the resolved directory path.
    """
    raise NotImplementedError
