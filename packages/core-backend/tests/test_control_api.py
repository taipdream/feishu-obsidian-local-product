from fastapi.testclient import TestClient

from feishu_obsidian_local_backend.control_api import app


def test_status_endpoint_returns_product_health_shape():
    client = TestClient(app)

    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()
    assert "backend_running" in data
    assert "vault_ready" in data
    assert "feishu_connected" in data
