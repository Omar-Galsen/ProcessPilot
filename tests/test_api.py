from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_pipe():
    response = client.post("/calculate/pipe", json={"length_m": 100, "diameter_m": 0.1, "velocity_m_s": 2, "density_kg_m3": 1000, "viscosity_pa_s": 0.001})
    assert response.status_code == 200
    assert response.json()["pressure_drop_pa"] > 0
