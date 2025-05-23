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
    # Prueba de inserción válida
    data = {"profile": "default", "message": "Mensaje insertado por test automático."}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Conversation created"

    # Prueba de inserción inválida (falta profile)
    data = {"message": "Sin perfil"}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 400
    assert "error" in response.get_json()

    # Prueba de inserción inválida (falta message)
    data = {"profile": "default"}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 400
    assert "error" in response.get_json()

    # Verificar que el mensaje insertado aparece en el GET
    response = client.get("/api/conversations?profile=default&limit=100")
    assert response.status_code == 200
    mensajes = [conv["message"] for conv in response.get_json()["data"]]
    assert "Mensaje insertado por test automático." in mensajes

    # Prueba de inserción con caracteres especiales y unicode
    data = {"profile": "unicode", "message": "¡Mensaje con acentos y emojis 😃!"}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Conversation created"
    response = client.get("/api/conversations?profile=unicode")
    assert response.status_code == 200
    mensajes = [conv["message"] for conv in response.get_json()["data"]]
    assert "¡Mensaje con acentos y emojis 😃!" in mensajes

    # Prueba de inserción con un perfil diferente
    data = {"profile": "otro", "message": "Mensaje para otro perfil"}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    response = client.get("/api/conversations?profile=otro")
    assert response.status_code == 200
    mensajes = [conv["message"] for conv in response.get_json()["data"]]
    assert "Mensaje para otro perfil" in mensajes

    # Prueba de paginación: insertar varios mensajes y comprobar el límite
    for i in range(15):
        data = {"profile": "paginacion", "message": f"Mensaje {i}"}
        client.post("/api/conversations", json=data)
    response = client.get("/api/conversations?profile=paginacion&limit=10")
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 10
    response = client.get("/api/conversations?profile=paginacion&limit=5&offset=10")
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 5

    # Prueba de inserción masiva y verificación de paginación y unicidad
    mensajes_masivos = [f"Mensaje masivo {i}" for i in range(30)]
    for msg in mensajes_masivos:
        data = {"profile": "masivo", "message": msg}
        response = client.post("/api/conversations", json=data)
        assert response.status_code == 201
    # Verificar paginación
    response = client.get("/api/conversations?profile=masivo&limit=10")
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 10
    # Verificar que todos los mensajes están presentes usando varias páginas
    todos = set()
    for offset in range(0, 30, 10):
        response = client.get(
            f"/api/conversations?profile=masivo&limit=10&offset={offset}"
        )
        assert response.status_code == 200
        todos.update(conv["message"] for conv in response.get_json()["data"])
    assert set(mensajes_masivos) == todos

    # Prueba de inserción de datos vacíos
    response = client.post("/api/conversations", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()

    # Prueba de inserción con tipos incorrectos
    data = {"profile": 123, "message": ["no", "string"]}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 400 or response.status_code == 500


def test_invalid_endpoint(client):
    response = client.get("/api/nonexistent-endpoint")
    assert response.status_code == 404
