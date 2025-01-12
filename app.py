import sqlite3
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Ruta principal
@app.route("/")
def home():
    return "API de gestión de conversaciones activa."


# Obtener conversaciones (GET)
@app.route("/api/conversations", methods=["GET"])
def get_conversations():
    profile = request.args.get("profile", "default")
    try:
        connection = sqlite3.connect("conversations.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM conversations WHERE profile = ?", (profile,))
        rows = cursor.fetchall()
        connection.close()
        if rows:
            return jsonify({"status": "success", "data": rows})
        else:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "No se encontraron conversaciones para este perfil.",
                    }
                ),
                404,
            )
    except sqlite3.Error as e:
        return (
            jsonify(
                {"status": "error", "message": f"Error en la base de datos: {str(e)}"}
            ),
            500,
        )


# Añadir conversación (POST)
@app.route("/api/conversations", methods=["POST"])
def post_conversation():
    data = request.get_json()
    profile = data.get("profile")
    message = data.get("message")

    if not profile or not message:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "El perfil y el mensaje son obligatorios.",
                }
            ),
            400,
        )

    try:
        connection = sqlite3.connect("conversations.db")
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO conversations (profile, message) VALUES (?, ?)",
            (profile, message),
        )
        connection.commit()
        connection.close()
        return jsonify({"status": "success", "message": "Conversación guardada."}), 201
    except sqlite3.Error as e:
        return (
            jsonify(
                {"status": "error", "message": f"Error en la base de datos: {str(e)}"}
            ),
            500,
        )


# Manejo de rutas no existentes
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"status": "error", "message": "Endpoint no encontrado."}), 404


if __name__ == "__main__":
    app.run(debug=True)

