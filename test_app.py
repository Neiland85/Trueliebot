"""
Pruebas automáticas para la API de TruelieBot.
Incluye pruebas de endpoints, validaciones y lógica de negocio.
"""


import json
from typing import Literal
import pytest
from unittest.mock import patch

from app import app, conversations_bp


@pytest.fixture
def client():
    # Registrar blueprint si no está registrado
    if "conversations" not in app.blueprints:
        app.register_blueprint(conversations_bp)
    with app.test_client() as client:
        yield client


def test_home(client: Any):
    """Prueba que la página de inicio carga correctamente."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'API de gestión de conversaciones activa.' in response.data.decode('utf-8')


def test_invalid_endpoint(client: Any):
    """Prueba el manejo de un endpoint inexistente."""
    response = client.get('/api/nonexistent-endpoint')
    assert response.status_code == 404


@patch("openai.ChatCompletion.create")
def test_openai_chat(mock_openai, client: Any):
    """Prueba la integración con la API de OpenAI para generación de respuestas (mockeada)."""
    # Mock OpenAI API response
    mock_openai.return_value = {
        "choices": [{"message": {"content": "París"}}]
    }
    response = client.post(
        "/api/openai",
        data=json.dumps({"prompt": "¿Cuál es la capital de Francia?"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "response" in data
    assert "París" in data.get("response", "")


@pytest.mark.parametrize("keyword_variant,message", [
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
])
def test_keyword_detection_variants(client: Any, keyword_variant: Literal['microexpresión'] | Literal['microexpresion'] | Literal['MICROEXPRESIÓN'] | Literal['cognitivo'] | Literal['carga cognitiva'] | Literal['resonancia'] | Literal['fmri'] | Literal['paraverbal'] | Literal['verbal'] | Literal['scan'] | Literal['inteligencia artificial'] | Literal['ia'] | Literal['emocional'] | Literal['emoción'], message: Literal['El análisis de microexpresión es útil.'] | Literal['Las microexpresion faciales son clave.'] | Literal['MICROEXPRESIÓN en mayúsculas.'] | Literal['El esfuerzo cognitivo aumenta al mentir.'] | Literal['La carga cognitiva es un indicador.'] | Literal['La resonancia cerebral detecta mentiras.'] | Literal['El uso de fMRI es común en estudios.'] | Literal['El análisis paraverbal ayuda.'] | Literal['Las señales verbales pueden delatar.'] | Literal['El método SCAN es efectivo.'] | Literal['La inteligencia artificial detecta patrones.'] | Literal['La IA supera a humanos en precisión.'] | Literal['El control emocional es difícil al mentir.'] | Literal['La emoción se filtra en la mentira.']):
    """Debe detectar variantes de palabras clave y devolver cita y consejos."""
    data = {"profile": "test", "message": message}
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "study_citation" in json_data
    assert "study_summary" in json_data
    assert "advice" in json_data
    assert isinstance(json_data["advice"], list)


def test_multiple_keywords_in_message(client: Any):
    """Si hay varias palabras clave, debe devolver la cita del primer match."""
    data = {
        "profile": "test",
        "message": "La microexpresión y la carga cognitiva son importantes.",
    }
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    # Debe devolver la cita de microexpresión (primer match en la lista de keywords)
    assert "Ekman" in json_data.get("study_citation", "")
    assert "microexpresiones" in json_data.get("study_summary", "")
    assert "advice" in json_data


def test_no_keyword_no_citation(client: Any):
    """No debe devolver cita ni consejos si no hay palabra clave relevante."""
    data = {
        "profile": "test",
        "message": "Este mensaje es completamente neutro y no contiene palabras clave.",
    }
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "study_citation" not in json_data
    assert "advice" not in json_data


def test_edge_cases_keywords(client: Any):
    """Prueba casos límite: palabra clave como parte de otra palabra, mensaje vacío, solo símbolos, repetición."""
    # Palabra clave como parte de otra palabra irrelevante
    data = {
        "profile": "test",
        "message": "microexpresionismo no es lo mismo que microexpresión.",
    }
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
    data = {
        "profile": "test",
        "message": "microexpresión microexpresión microexpresión",
    }
    response = client.post("/api/conversations", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "study_citation" in json_data
