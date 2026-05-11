import re

from beehave.traceability import sync


def test_sync_2b8e4a7d(tmp_path) -> None:
    """Sync assigns unique random 8-character @id tags to all scenarios lacking them.

    Given a .feature file with three scenarios, none having @id tags
    When the developer runs beehave sync
    Then each scenario gets a unique random 8-character @id tag
    And the .feature file is updated with the new tags
    """
    feature_path = tmp_path / "test.feature"
    feature_path.write_text(
        "Feature: Test\n"
        "  Rule: R1\n"
        "    Example: S1\n"
        "      Given something\n"
        "    Example: S2\n"
        "      Given something\n"
        "    Example: S3\n"
        "      Given something\n"
    )
    sync(str(feature_path))
    result = feature_path.read_text()
    ids = [
        line.strip() for line in result.splitlines() if line.strip().startswith("@id:")
    ]
    assert len(ids) == 3
    id_values = [line.split(":")[1] for line in ids]
    assert len(set(id_values)) == 3
    for v in id_values:
        assert len(v) == 8
        assert all(c in "0123456789abcdef" for c in v)


def test_sync_9c3f6e1a(tmp_path) -> None:
    """Sync replaces malformed or manual @id tags with beehave-generated random IDs.

    Given a .feature scenario with @id:my_custom_name
    When the developer runs beehave sync
    Then beehave replaces @id:my_custom_name with a beehave-generated 8-char random ID
    """
    feature_path = tmp_path / "test.feature"
    feature_path.write_text(
        "Feature: Test\n"
        "  Rule: R1\n"
        "    @id:my_custom_name\n"
        "    Example: S1\n"
        "      Given something\n"
    )
    sync(str(feature_path))
    result = feature_path.read_text()
    assert "@id:my_custom_name" not in result
    new_ids = re.findall(r"@id:([0-9a-f]{8})", result)
    assert len(new_ids) == 1


def test_sync_5a7d2b8f(tmp_path) -> None:
    """Running sync on an already-synced file produces no changes.

    Given a .feature file where all scenarios already have beehave-generated @id tags
    When the developer runs beehave sync
    Then no changes are made to the .feature file
    """
    feature_path = tmp_path / "test.feature"
    original = (
        "Feature: Test\n"
        "  Rule: R1\n"
        "    @id:abcdef12\n"
        "    Example: S1\n"
        "      Given something\n"
    )
    feature_path.write_text(original)
    sync(str(feature_path))
    result = feature_path.read_text()
    assert result == original
