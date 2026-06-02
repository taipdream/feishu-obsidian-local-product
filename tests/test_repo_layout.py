from pathlib import Path


def test_product_repo_contains_expected_top_level_units():
    root = Path(__file__).resolve().parents[1]
    expected = [
        "apps/macos-shell",
        "packages/core-backend",
        "packages/obsidian-plugin",
        "assets/starter-vault",
    ]
    missing = [item for item in expected if not (root / item).exists()]
    assert missing == []


def test_unsigned_install_docs_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "docs" / "installing-unsigned-builds.md").exists()
