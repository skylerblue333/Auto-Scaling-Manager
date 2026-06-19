from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_scale_up():
    r = client.post("/api/v1/evaluate", json={"service": "api", "cpu_percent": 90, "memory_percent": 70})
    assert r.status_code == 200
    assert r.json()["action"] == "scale_up"

def test_scale_down():
    r = client.post("/api/v1/evaluate", json={"service": "api", "cpu_percent": 10, "memory_percent": 15})
    assert r.status_code == 200
    assert r.json()["action"] == "scale_down"

