"""
Pruebas automáticas para la API de TruelieBot.
Incluye pruebas de endpoints, validaciones y lógica de negocio.
"""

import pytest
import json
from app import app
from unittest.mock import patch


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_home(client):
    """Prueba que la página de inicio carga correctamente."""
    response = client.get("/")
    assert "API de gestión de conversaciones activa." in response.data.decode("utf-8")


def test_get_conversations(client):
    """Prueba la obtención de conversaciones con el perfil por defecto."""
    response = client.get("/api/conversations?profile=default")
    assert response.status_code in [200, 404]


def test_post_conversations(client):
    """Prueba la creación de conversaciones con diferentes escenarios."""
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


def test_post_conversations_with_advice(client):
    """Debe devolver cita científica y consejos si el mensaje contiene una palabra clave de manipulación."""
    data = {"profile": "test", "message": "El análisis de microexpresion es clave para detectar mentiras."}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "study_citation" in json_data
    assert "study_summary" in json_data
    assert "advice" in json_data
    assert isinstance(json_data["advice"], list)
    assert any("calma" in consejo.lower() for consejo in json_data["advice"])


def test_invalid_endpoint(client):
    """Prueba el manejo de un endpoint inexistente."""
    response = client.get("/api/nonexistent-endpoint")
    assert response.status_code == 404


@patch("openai.ChatCompletion.create")
def test_openai_chat(mock_openai, client):
    """Prueba la integración con la API de OpenAI para generación de respuestas (mockeada)."""
    # Mock OpenAI API response
    mock_openai.return_value = type("obj", (object,), {"__str__": lambda self: '{"choices": [{"message": {"content": "París"}}]}'})()
    response = client.post(
        "/api/openai",
        data=json.dumps({"prompt": "¿Cuál es la capital de Francia?"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "response" in data
    assert "París" in data.get("response", "")


def pytest_generate_tests(metafunc):
    # Parametrización dinámica para variantes de palabras clave
    if "keyword_variant" in metafunc.fixturenames:
        variants = [
            # microexpresión
            ("microexpresión", "El análisis de microexpresión es útil."),
            ("microexpresion", "Las microexpresion faciales son clave."),
            ("MICROEXPRESIÓN", "MICROEXPRESIÓN en mayúsculas."),
            # carga cognitiva
            ("cognitivo", "El esfuerzo cognitivo aumenta al mentir."),
            ("carga cognitiva", "La carga cognitiva es un indicador."),
            # fMRI
            ("resonancia", "La resonancia cerebral detecta mentiras."),
            ("fmri", "El uso de fMRI es común en estudios."),
            # verbal
            ("paraverbal", "El análisis paraverbal ayuda."),
            ("verbal", "Las señales verbales pueden delatar."),
            # SCAN
            ("scan", "El método SCAN es efectivo."),
            # IA
            ("inteligencia artificial", "La inteligencia artificial detecta patrones."),
            ("ia", "La IA supera a humanos en precisión."),
            # emoción
            ("emocional", "El control emocional es difícil al mentir."),
            ("emoción", "La emoción se filtra en la mentira."),
        ]
        metafunc.parametrize("keyword_variant,message", variants)


def test_keyword_detection_variants(client, keyword_variant, message):
    """Debe detectar variantes de palabras clave y devolver cita y consejos."""
    data = {"profile": "test", "message": message}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "study_citation" in json_data
    assert "study_summary" in json_data
    assert "advice" in json_data
    assert isinstance(json_data["advice"], list)


def test_multiple_keywords_in_message(client):
    """Si hay varias palabras clave, debe devolver la cita del primer match."""
    data = {"profile": "test", "message": "La microexpresión y la carga cognitiva son importantes."}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    # Debe devolver la cita de microexpresión (primer match en la lista de keywords)
    assert "Ekman" in json_data.get("study_citation", "")
    assert "microexpresiones" in json_data.get("study_summary", "")
    assert "advice" in json_data


def test_no_keyword_no_citation(client):
    """No debe devolver cita ni consejos si no hay palabra clave relevante."""
    data = {"profile": "test", "message": "Este mensaje es completamente neutro y no contiene palabras clave."}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "study_citation" not in json_data
    assert "advice" not in json_data


def test_edge_cases_keywords(client):
    """Prueba casos límite: palabra clave como parte de otra palabra, mensaje vacío, solo símbolos, repetición."""
    # Palabra clave como parte de otra palabra irrelevante
    data = {"profile": "test", "message": "microexpresionismo no es lo mismo que microexpresión."}
    response = client.post("/api/conversations", json=data)
    # Debe detectar microexpresión porque está presente como palabra
    json_data = response.get_json()
    assert response.status_code == 201
    assert "study_citation" in json_data
    # Mensaje vacío
    data = {"profile": "test", "message": ""}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "study_citation" not in json_data
    # Solo símbolos
    data = {"profile": "test", "message": "!!!@@@###"}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "study_citation" not in json_data
    # Palabra clave repetida
    data = {"profile": "test", "message": "microexpresión microexpresión microexpresión"}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "study_citation" in json_data
