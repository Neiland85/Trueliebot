"""
Módulo principal de la aplicación Flask para TruelieBot.
Se encarga de inicializar la app, registrar blueprints y exponer la documentación Swagger.
"""

from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from routes_conversations import conversations_bp

app = Flask(__name__)
app.register_blueprint(conversations_bp)


@app.route("/", methods=["GET"])
def home():
    """Endpoint raíz para verificar el estado de la API."""
    return "API de gestión de conversaciones activa.", 200


@app.route("/favicon.ico")
def favicon():
    """Sirve el favicon para evitar errores 404 en navegadores."""
    return send_from_directory(
        app.root_path,
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


# Swagger/OpenAPI docs
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "TruelieBot API"},
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == "__main__":
    app.run(debug=True)
