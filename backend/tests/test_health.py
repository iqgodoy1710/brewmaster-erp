from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_returns_welcome_message():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Bienvenido a BrewMaster ERP"
    }