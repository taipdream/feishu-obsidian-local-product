from fastapi.testclient import TestClient

from feishu_obsidian_local_backend.control_api import app


def test_status_endpoint_exposes_action_needed_flag():
    client = TestClient(app)
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "action_needed" in data
