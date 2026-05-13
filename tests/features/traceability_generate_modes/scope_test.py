import os


def test_traceability_generate_modes_f2d4a6b8(tmp_path, monkeypatch) -> None:
    """Generate processes all features by default, single feature by name.

    Given a project with multiple .feature files in docs/features/
    When the developer runs beehave generate
    Then all .feature files are processed and orphan scenarios receive test stubs

    Given a project with multiple .feature files in docs/features/
    When the developer runs beehave generate balance_accounting
    Then only balance_accounting.feature is processed
    """
    from beehave.cli import _discover_feature_files

    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "balance_accounting.feature").write_text(
        "Feature: Balance\n  @id:aaa11111\n  Example: One\n    Given x\n"
    )
    (features_dir / "inventory_mgmt.feature").write_text(
        "Feature: Inventory\n  @id:bbb22222\n  Example: Two\n    Given y\n"
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    # No feature_name → discovers all .feature files
    all_files = _discover_feature_files()
    names = sorted(os.path.basename(f) for f in all_files)
    assert names == ["balance_accounting.feature", "inventory_mgmt.feature"]

    # With feature_name → discovers only that one
    single_files = _discover_feature_files("balance_accounting")
    assert len(single_files) == 1
    assert single_files[0].endswith("balance_accounting.feature")
