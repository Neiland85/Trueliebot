import pytest
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "API de gestión de conversaciones activa." in response.data.decode('utf-8')

def test_get_conversations(client):
    response = client.get('/api/conversations?profile=default')
    assert response.status_code in [200, 404]
    if response.status_code == 200:   
        assert "data" in response.json
    else:
        assert "status" in response.json
        assert response.json["status"] == "error"

class MockChoice:
    def __init__(self, text):
        self.text = text

class MockOpenAIResponse:
    def __init__(self, text):
        self.choices = [MockChoice(text)]

@patch('app.openai.Completion.create')
def test_post_ask(mock_create, client):
    mock_create.return_value = MockOpenAIResponse("Python es un lenguaje de programación.")
    response = client.post('/api/ask', json={"question": "¿Qué es Python?"})
    assert response.status_code == 200
    assert "answer" in response.json
    assert "lenguaje de programación" in response.json["answer"]

@patch('app.openai.Completion.create')
def test_post_ask_invalid_key(mock_create, client):
    mock_create.side_effect = Exception("Incorrect API key provided")

    response = client.post('/api/ask', json={"question": "¿Qué es Python?"})
    assert response.status_code == 500
    assert "status" in response.json
    assert response.json["status"] == "error"
    assert "message" in response.json
    assert "Incorrect API key" in response.json["message"]

