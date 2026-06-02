from pathlib import Path


def test_backend_bundle_layout_contains_runtime_entrypoint():
    root = Path(__file__).resolve().parents[1]
    bundle = root / "dist" / "backend-bundle"
    assert (bundle / "run_backend").exists()


def test_backend_bundle_entrypoint_mentions_status_api_server():
    root = Path(__file__).resolve().parents[1]
    entrypoint = root / "dist" / "backend-bundle" / "run_backend"
    text = entrypoint.read_text(encoding="utf-8")
    assert "uvicorn" in text
    assert "control_api:app" in text
