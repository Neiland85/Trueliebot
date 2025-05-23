"""
Módulo de utilidades para la gestión de la base de datos SQLite.
Separa la lógica de acceso a datos de la lógica de rutas Flask.
"""
import sqlite3
from typing import List, Dict, Any

DB_NAME = "conversations.db"


def get_db_connection():
    """Crea y retorna una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_conversations(
    profile: str, limit: int = 20, offset: int = 0
) -> List[Dict[str, Any]]:
    """Obtiene conversaciones para un perfil dado, con paginación."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM conversations WHERE profile = ? LIMIT ? OFFSET ?",
            (profile, limit, offset),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def insert_conversation(profile: str, message: str) -> None:
    """Inserta una nueva conversación en la base de datos."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (profile, message) VALUES (?, ?)",
            (profile, message),
        )
        conn.commit()
