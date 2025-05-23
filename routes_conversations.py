from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from db import fetch_conversations, insert_conversation

conversations_bp = Blueprint("conversations", __name__)


class ConversationSchema(Schema):
    profile = fields.Str(required=True)
    message = fields.Str(required=True)


conversation_schema = ConversationSchema()


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
            return (
                jsonify({"data": conversations, "status": "success"}),
                200,
            )
        return jsonify({"message": "No conversations found"}), 404
    except Exception as e:
        return (
            jsonify({"error": f"Internal Server Error: {str(e)}"}),
            500,
        )


@conversations_bp.route("/api/conversations", methods=["POST"])
def post_conversations():
    """Crea una nueva conversación."""
    try:
        data = request.get_json()
        try:
            validated = conversation_schema.load(data)
            if not isinstance(validated, dict):
                raise ValidationError("Datos no válidos")
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400
        profile = validated.get("profile")
        message = validated.get("message")
        if not isinstance(profile, str) or not isinstance(message, str):
            return jsonify({"error": "Los campos deben ser cadenas de texto."}), 400
        insert_conversation(profile, message)
        return jsonify({"message": "Conversation created"}), 201
    except Exception as e:
        return (
            jsonify({"error": f"Internal Server Error: {str(e)}"}),
            500,
        )
