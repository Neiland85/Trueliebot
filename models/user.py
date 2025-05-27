"""
Modelos relacionados con usuarios para TruelieBot.

Este módulo proporciona funciones para gestionar usuarios,
autenticación y validación de credenciales.
"""

import binascii
import hashlib
import os
import sqlite3
from typing import Any, Dict, Optional, Tuple

# Constantes para configuración de seguridad
HASH_ALGORITHM = "sha512"
HASH_ITERATIONS = 100000
SALT_SIZE = 60  # Tamaño del salt en bytes


def hash_password(password: str) -> str:
    """
    Genera un hash seguro para la contraseña.

    Args:
        password: Contraseña en texto plano

    Returns:
        Hash de la contraseña con sal
    """
    # Generar salt aleatorio
    salt = hashlib.sha256(os.urandom(SALT_SIZE)).hexdigest().encode("ascii")

    # Generar hash usando el salt
    pwdhash = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM, password.encode("utf-8"), salt, HASH_ITERATIONS
    )
    pwdhash = binascii.hexlify(pwdhash)

    # Combinar salt y hash
    return (salt + pwdhash).decode("ascii")


def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verifica si una contraseña coincide con un hash almacenado.

    Args:
        stored_password: Hash almacenado
        provided_password: Contraseña a verificar

    Returns:
        True si la contraseña coincide, False en caso contrario
    """
    # Extraer salt del hash almacenado
    salt = stored_password[:64]
    stored_hash = stored_password[64:]

    # Calcular hash de la contraseña proporcionada con el mismo salt
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
    )
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")

    # Comparar hashes
    return pwdhash == stored_hash


def get_user_by_id(conn: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un usuario por su ID.

    Args:
        conn: Conexión a la base de datos
        user_id: ID del usuario

    Returns:
        Datos del usuario o None si no existe
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nombre, email, password_hash, rol, activo, fecha_creacion
        FROM usuarios
        WHERE id = ?
    """,
        (user_id,),
    )

    user = cursor.fetchone()
    if not user:
        return None

    return {
        "id": user[0],
        "nombre": user[1],
        "email": user[2],
        "password_hash": user[3],
        "rol": user[4],
        "activo": bool(user[5]),
        "fecha_creacion": user[6],
    }


def get_user_by_email_or_nombre(
    conn: sqlite3.Connection, usuario_id: str
) -> Optional[Dict[str, Any]]:
    """
    Obtiene un usuario por su email o nombre de usuario.

    Args:
        conn: Conexión a la base de datos
        usuario_id: Email o nombre de usuario

    Returns:
        Datos del usuario o None si no existe
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nombre, email, password_hash, rol, activo, fecha_creacion
        FROM usuarios
        WHERE email = ? OR nombre = ?
    """,
        (usuario_id, usuario_id),
    )

    user = cursor.fetchone()
    if not user:
        return None

    return {
        "id": user[0],
        "nombre": user[1],
        "email": user[2],
        "password_hash": user[3],
        "rol": user[4],
        "activo": bool(user[5]),
        "fecha_creacion": user[6],
    }


def validate_credentials(
    conn: sqlite3.Connection, usuario_id: str, password: str
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Valida las credenciales de un usuario usando email o nombre de usuario.

    Args:
        conn: Conexión a la base de datos
        usuario_id: Email o nombre de usuario
        password: Contraseña proporcionada

    Returns:
        Tupla (éxito, datos de usuario) donde éxito es un booleano
        y datos de usuario son los datos del usuario si las credenciales son válidas
    """
    user = get_user_by_email_or_nombre(conn, usuario_id)

    if not user:
        return False, None

    if not user["activo"]:
        return False, None

    if verify_password(user["password_hash"], password):
        # No incluir password_hash en los datos devueltos
        del user["password_hash"]
        return True, user

    return False, None


def create_user(
    conn: sqlite3.Connection, nombre: str, email: str, password: str, rol: str = "user"
) -> int:
    """
    Crea un nuevo usuario en la base de datos.

    Args:
        conn: Conexión a la base de datos
        nombre: Nombre del usuario
        email: Email del usuario
        password: Contraseña en texto plano
        rol: Rol del usuario (user o admin)

    Returns:
        ID del usuario creado

    Raises:
        ValueError: Si el email ya está en uso
    """
    cursor = conn.cursor()

    # Verificar si el email ya existe
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    if cursor.fetchone():
        cursor.close()
        raise ValueError("El email ya está en uso")

    # Hash de la contraseña
    password_hash = hash_password(password)

    # Insertar usuario
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, email, password_hash, rol, activo)
            VALUES (?, ?, ?, ?, 1)
        """,
            (nombre, email, password_hash, rol),
        )
        conn.commit()
        user_id = cursor.lastrowid
    finally:
        cursor.close()
    return user_id
