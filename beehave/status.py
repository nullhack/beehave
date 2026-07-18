from pathlib import Path


def status(root: Path) -> int:
    features_dir = root / "docs" / "features"
    if not features_dir.is_dir():
        return 2
    feature_count = len(list(features_dir.glob("*.feature")))
    tests_dir = root / "tests"
    stub_count = len(list(tests_dir.glob("*_test.pyi"))) if tests_dir.is_dir() else 0
    print(f"{feature_count} feature file(s)")
    print(f"{stub_count} stub file(s)")
    return 0
