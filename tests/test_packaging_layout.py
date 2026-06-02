from pathlib import Path


def test_build_script_output_contains_expected_app_paths():
    root = Path(__file__).resolve().parents[1]
    app_root = root / "dist" / "app" / "FeishuObsidianLocal.app"

    assert (app_root / "Contents" / "MacOS" / "FeishuObsidianLocal").exists()
    assert (app_root / "Contents" / "Resources" / "backend-bundle" / "run_backend").exists()


def test_release_artifacts_exist_after_packaging():
    root = Path(__file__).resolve().parents[1]
    releases = root / "dist" / "releases"

    assert (releases / "FeishuObsidianLocal-macos.zip").exists()
    assert (releases / "FeishuObsidianLocal-macos.dmg").exists()
