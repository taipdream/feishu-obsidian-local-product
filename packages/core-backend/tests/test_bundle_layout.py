from pathlib import Path


def test_backend_bundle_layout_contains_runtime_entrypoint():
    root = Path(__file__).resolve().parents[1]
    bundle = root / "dist" / "backend-bundle"
    assert (bundle / "run_backend").exists()
