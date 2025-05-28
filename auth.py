"""
Módulo de autenticación para TruelieBot.

Este módulo proporciona funciones para autenticar usuarios y proteger
endpoints sensibles usando JWT (JSON Web Tokens).
"""

import datetime
import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

# Importaciones condicionales para manejar dependencias opcionales
try:
    import jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logging.warning(
        "ADVERTENCIA: PyJWT no está instalado. La autenticación estará desactivada."
    )
    logging.warning("Para habilitar la autenticación, instala PyJWT: pip install PyJWT")

from flask import Flask, current_app, jsonify, request

# Constantes de configuración
TOKEN_HEADER = "Authorization"
TOKEN_PREFIX = "Bearer "
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("La variable de entorno JWT_SECRET_KEY es obligatoria para la seguridad JWT.")
TOKEN_EXPIRATION_MINUTES = int(os.environ.get("TOKEN_EXPIRATION_MINUTES", 60))

# Configurar mensajes de error
AUTH_ERRORS = {
    "token_required": {
        "message": "Token de autenticación requerido",
        "error": "Unauthorized",
    },
    "token_expired": {"message": "Token expirado", "error": "Token expired"},
    "token_invalid": {"message": "Token inválido", "error": "Invalid token"},
    "admin_required": {
        "message": "Se requieren privilegios de administrador",
        "error": "Forbidden",
    },
}


def initialize_auth(app: Flask) -> None:
    """
    Inicializa la configuración de autenticación en la aplicación Flask.

    Args:
        app: Instancia de aplicación Flask
    """
    # Guardar configuración en app
    app.config["JWT_SECRET_KEY"] = SECRET_KEY
    app.config["JWT_TOKEN_EXPIRATION"] = TOKEN_EXPIRATION_MINUTES

    # Agregar información de autenticación a la documentación Swagger
    try:
        swagger_path = os.path.join(os.path.dirname(__file__), "static", "swagger.json")
        if os.path.exists(swagger_path):
            import json

            with open(swagger_path, "r") as f:
                swagger_data = json.load(f)

            # Añadir seguridad a Swagger
            swagger_data["securityDefinitions"] = {
                "bearerAuth": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                }
            }

            # Marcar endpoints sensibles como protegidos
            for path in swagger_data.get("paths", {}):
                if any(
                    endpoint in path
                    for endpoint in [
                        "/api/feedback",
                        "/api/patrones",
                        "/api/estadisticas",
                    ]
                ):
                    for method in swagger_data["paths"][path]:
                        swagger_data["paths"][path][method]["security"] = [
                            {"bearerAuth": []}
                        ]

            with open(swagger_path, "w") as f:
                json.dump(swagger_data, f, indent=2)
    except Exception as e:
        print(f"No se pudo actualizar la documentación Swagger: {e}")


def generate_token(user_id: int, role: str = "user") -> str:
    """
    Genera un token JWT para un usuario.

    Args:
        user_id: ID del usuario
        role: Rol del usuario (user, admin)

    Returns:
        Token JWT generado
    """
    if not JWT_AVAILABLE:
        return "jwt-disabled"

    payload = {
        "user_id": user_id,
        "role": role,
        "exp": (
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
        ),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifica un token JWT y devuelve su contenido.

    Args:
        token: Token JWT a verificar

    Returns:
        Contenido del token si es válido

    Raises:
        jwt.InvalidTokenError: Si el token no es válido
    """
    if not JWT_AVAILABLE:
        return {"user_id": 0, "role": "user"}

    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


def token_required(f: Callable) -> Callable:
    """
    Decorador que verifica que se proporcione un token JWT válido.

    Args:
        f: Función a decorar

    Returns:
        Función decorada
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Si JWT no está disponible, permitir acceso (modo desarrollo)
        if not JWT_AVAILABLE:
            current_app.logger.warning(
                "PyJWT no está instalado. Permitiendo acceso sin autenticación."
            )
            return f(user_data={"user_id": 0, "role": "user"}, *args, **kwargs)

        # Obtener token del header Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return (
                jsonify(
                    {
                        "message": "Token de autenticación requerido",
                        "error": "Unauthorized",
                    }
                ),
                401,
            )

        try:
            # Verificar token
            data = verify_token(token)
            # Pasar los datos del token a la función decorada
            return f(user_data=data, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expirado", "error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token inválido", "error": "Invalid token"}), 401

    return decorated


def admin_required(f: Callable) -> Callable:
    """
    Decorador que verifica que el usuario tenga rol de administrador.

    Args:
        f: Función a decorar

    Returns:
        Función decorada
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Si JWT no está disponible, permitir acceso (modo desarrollo)
        if not JWT_AVAILABLE:
            current_app.logger.warning(
                "PyJWT no está instalado. Permitiendo acceso sin autenticación."
            )
            return f(user_data={"user_id": 0, "role": "admin"}, *args, **kwargs)

        # Obtener token del header Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return (
                jsonify(
                    {
                        "message": "Token de autenticación requerido",
                        "error": "Unauthorized",
                    }
                ),
                401,
            )

        try:
            # Verificar token
            data = verify_token(token)

            # Verificar rol de administrador
            if data.get("role") != "admin":
                return (
                    jsonify(
                        {
                            "message": "Se requieren privilegios de administrador",
                            "error": "Forbidden",
                        }
                    ),
                    403,
                )

            # Pasar los datos del token a la función decorada
            return f(user_data=data, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expirado", "error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token inválido", "error": "Invalid token"}), 401

    return decorated


# Endpoint para generar tokens de autenticación
def create_auth_routes(app: Flask) -> None:
    """
    Crea las rutas de autenticación en la aplicación Flask.

    Args:
        app: Aplicación Flask
    """

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        """Endpoint para iniciar sesión y obtener un token JWT."""
        if not request.is_json:
            return (
                jsonify(
                    {"message": "Se esperaba un cuerpo JSON", "error": "Bad request"}
                ),
                400,
            )

        try:
            # Validar datos de entrada
            data = request.get_json()

            # Usar esquema Marshmallow para validación
            try:
                from schemas import LoginSchema
                from marshmallow import ValidationError  # <-- Mover esta importación fuera del try

            except ImportError as err:
                return (
                    jsonify(
                        {
                            "message": "Error importando dependencias de validación",
                            "error": str(err),
                        }
                    ),
                    500,
                )

            try:
                login_data = LoginSchema().load(data)
            except ValidationError as err:
                return (
                    jsonify(
                        {
                            "message": "Datos de login inválidos",
                            "errors": err.messages,
                            "error": "Bad request",
                        }
                    ),
                    400,
                )

            from db import get_db_connection

            conn = get_db_connection()
            try:
                # Importar función de validación
                from models.user import validate_credentials

                # Validar credenciales contra la base de datos
                success, user = validate_credentials(
                    conn, login_data["username"], login_data["password"]
                )

                if success and user:
                    # Generar token
                    token = generate_token(user["id"], user["role"])

                    return jsonify(
                        {
                            "token": token,
                            "user_id": user["id"],
                            "nombre": user["nombre"],
                            "role": user["role"],
                            "expires_in": TOKEN_EXPIRATION_MINUTES * 60,
                        }
                    )
                else:
                    return (
                        jsonify(
                            {
                                "message": "Credenciales inválidas",
                                "error": "Unauthorized",
                            }
                        ),
                        401,
                    )
            finally:
                conn.close()

        except Exception as e:
            return (
                jsonify(
                    {
                        "message": f"Error en autenticación: {str(e)}",
                        "error": "Internal server error",
                    }
                ),
                500,
            )

    @app.route("/api/auth/verify", methods=["GET"])
    @token_required
    def verify(user_data):
        """
        Endpoint para verificar si un token es válido.

        Returns:
            Datos del usuario si el token es válido
        """
        return jsonify(
            {
                "message": "Token válido",
                "user_id": user_data.get("user_id"),
                "role": user_data.get("role"),
            }
        )
