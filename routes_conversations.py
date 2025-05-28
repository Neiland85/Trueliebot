"""
Rutas y lógica de negocio para la gestión de conversaciones y la integración con OpenAI.
Incluye validación, inserción, consulta y justificación científica automática.
"""

import json
import os
import re
import unicodedata

import openai
from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields

from advice_script import get_advice_script
from db import fetch_conversations, insert_conversation
from lie_detection_studies import get_study_citation_by_topic
from utils.keyword_detection import detect_keyword_and_science

conversations_bp = Blueprint("conversations", __name__)


class ConversationSchema(Schema):
    profile = fields.Str(required=True)
    message = fields.Str(required=True)


conversation_schema = ConversationSchema()
import pytest
from routes_conversations import normalize

@pytest.mark.parametrize(
    "text,expected",
    [
        # Happy path: accented characters
        ("Canción", "cancion"),
        ("niño", "nino"),
        ("Árbol", "arbol"),
        ("MÚSICA", "musica"),
        ("pingüino", "pinguino"),
        # Happy path: mixed case and special chars
        ("¡Hola, Señor!", "hola, senor!"),
        ("El café está frío.", "el cafe esta frio."),
        ("mañana será otro día", "manana sera otro dia"),
        # Happy path: already normalized
        ("python", "python"),
        ("12345", "12345"),
        # Edge: empty string
        ("", ""),
        # Edge: only accents
        ("áéíóúüñ", "aeiouun"),
        # Edge: only non-ASCII symbols
        ("©®™", ""),
        # Edge: whitespace only
        ("   ", "   "),
        # Edge: tabs and newlines
        ("\t\n", "\t\n"),
        # Edge: emoji and symbols
        ("hello 😊", "hello "),
        ("💡⚡", ""),
        # Edge: combining characters
        ("Cafe\u0301", "cafe"),  # 'e' + combining acute
        # Edge: mixed ASCII and non-ASCII
        ("España 2024!", "espana 2024!"),
        # Edge: non-Latin script
        ("Привет", ""),  # Cyrillic
        ("你好", ""),    # Chinese
        ("こんにちは", ""),  # Japanese
    ],
    ids=[
        "accented-cancion",
        "accented-nino",
        "accented-arbol",
        "upper-musica",
        "umlaut-pinguino",
        "punctuation-senor",
        "cafe-frio",
        "manana-sera",
        "already-normalized",
        "numbers-only",
        "empty-string",
        "only-accents",
        "only-non-ascii-symbols",
        "whitespace-only",
        "tabs-newlines",
        "emoji-in-text",
        "emoji-only",
        "combining-acute",
        "mixed-ascii-non-ascii",
        "cyrillic",
        "chinese",
        "japanese",
    ]
)
def test_normalize_various_cases(text, expected):

    # Act
    result = normalize(text)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "bad_input,expected_exception",
    [
        (None, TypeError),
        (123, TypeError),
        (["hola"], TypeError),
        ({"text": "hola"}, TypeError),
        (b"hola", TypeError),
    ],
    ids=[
        "none-input",
        "int-input",
        "list-input",
        "dict-input",
        "bytes-input",
    ]
)
def test_normalize_type_errors(bad_input, expected_exception):

    # Act & Assert
    with pytest.raises(expected_exception):
        normalize(bad_input)


def normalize(text: str) -> str:
    """
    Normaliza un texto eliminando tildes, convirtiendo a minúsculas y eliminando caracteres no ASCII.
    """
    return (
        unicodedata.normalize("NFKD", text)
        .encode("ASCII", "ignore")
        .decode("utf-8")
        .lower()
    )


@conversations_bp.route("/api/conversations", methods=["GET"])
def get_conversations():
    """Obtiene conversaciones para un perfil dado, con paginación."""
    try:
        profile = request.args.get("profile", "default")
        try:
            limit = int(request.args.get("limit", 20))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return jsonify({"error": "Parámetros de paginación inválidos"}), 400

        conversations = fetch_conversations(profile, limit, offset)
        if conversations:
            return jsonify({"data": conversations, "status": "success"}), 200
        return jsonify({"message": "No conversations found"}), 404
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@conversations_bp.route("/api/conversations", methods=["POST"])
def post_conversations():
    """Crea una nueva conversación y cita estudios científicos si corresponde."""
    try:
        data = request.get_json()
        try:
            validated = conversation_schema.load(data)
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400

        profile = validated.get("profile")
        message = validated.get("message")
        insert_conversation(profile, message)

        normalized_message = normalize(message)
        keywords = [
            ("microexpresión", ["microexpresion", "microexpresión"]),
            ("carga cognitiva", ["cognitivo", "carga cognitiva"]),
            ("fMRI", ["resonancia", "fmri", "f m r i"]),
            ("verbal", ["paraverbal", "verbal", "verbales", "verbalidad"]),
            ("SCAN", ["scan"]),
            ("IA", ["inteligencia artificial", "ia"]),
            ("emoción", ["emocional", "emoción"]),
        ]

        result = detect_keyword_and_science(message)
        if result:
            return jsonify({"message": "Conversation created", **result}), 201
        return jsonify({"message": "Conversation created"}), 201
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@conversations_bp.route("/api/openai", methods=["POST"])
def openai_chat():
    """Endpoint para interactuar con OpenAI GPT usando un prompt enviado por el usuario."""
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "Falta el campo 'prompt'"}), 400

        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if os.environ.get("MOCK_OPENAI", "0") == "1":
            response_json = {"response": "París"}
        else:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                )
                answer = (
                    response.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                response_json = {"response": answer}
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        normalized_prompt = normalize(prompt)
        keywords = [
            ("microexpresión", ["microexpresion", "microexpresión"]),
            ("carga cognitiva", ["cognitivo", "carga cognitiva"]),
            ("fMRI", ["resonancia", "fmri", "f m r i"]),
            ("verbal", ["paraverbal", "verbal", "verbales", "verbalidad"]),
            ("SCAN", ["scan"]),
            ("IA", ["inteligencia artificial", "ia"]),
            ("emoción", ["emocional", "emoción"]),
        ]

        if result := detect_keyword_and_science(prompt):
            response_json |= result
        return jsonify(response_json)
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@conversations_bp.route("/api/advice", methods=["GET"])
def get_advice():
    """Devuelve un guion de consejos para víctimas de mentiras o manipulación."""
    try:
        return jsonify({"advice": get_advice_script()})
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@conversations_bp.route("/")
def home():
    return "API de gestión de conversaciones activa.", 200
