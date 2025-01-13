import pytest
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert "API de gestión de conversaciones activa." in response.data.decode("utf-8")


def test_get_conversations(client):
    response = client.get("/api/conversations?profile=default")
    assert response.status_code in [200, 404]


def test_post_conversations(client):
    data = {"profile": "default", "message": "Hola, esta es una prueba."}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201


def test_invalid_endpoint(client):
    response = client.get("/api/nonexistent-endpoint")
    assert response.status_code == 404

