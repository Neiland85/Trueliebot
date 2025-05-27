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

conversations_bp = Blueprint("conversations", __name__)


class ConversationSchema(Schema):
    profile = fields.Str(required=True)
    message = fields.Str(required=True)


conversation_schema = ConversationSchema()


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

        for topic, keyword_list in keywords:
            for k in keyword_list:
                k_norm = normalize(k)
                pattern = r"(^|\W)" + re.escape(k_norm) + r"(es|idad|al|ales)?($|\W)"
                if re.search(pattern, normalized_message):
                    cita, resumen = get_study_citation_by_topic(topic)
                    if cita:
                        return (
                            jsonify(
                                {
                                    "message": "Conversation created",
                                    "study_citation": cita,
                                    "study_summary": resumen,
                                    "advice": get_advice_script(),
                                }
                            ),
                            201,
                        )
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

        for topic, keyword_list in keywords:
            for k in keyword_list:
                k_norm = normalize(k)
                pattern = r"(^|\W)" + re.escape(k_norm) + r"(es|idad|al|ales)?($|\W)"
                if re.search(pattern, normalized_prompt):
                    cita, resumen = get_study_citation_by_topic(topic)
                    if cita and resumen:
                        response_json["study_citation"] = str(cita)
                        response_json["study_summary"] = str(resumen)
                        response_json["advice"] = "\n".join(get_advice_script())
                    break
            else:
                continue
            break
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


my_list = ["a", "b", "c"]
# Acceso por índice
value = (
    my_list[0] if my_list else None
)  # Accede al primer elemento si la lista no está vacía

if isinstance(my_object, dict):
    value = my_object.get("key", "default_value")
else:
    value = None  # Manejo de casos donde no es un diccionario

print(type(my_object))
