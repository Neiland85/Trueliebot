"""
Script para inicializar la base de datos SQLite con datos de prueba.
"""

import sqlite3


def initialize_database():
    """Crea la base de datos y la tabla de conversaciones con datos de ejemplo."""
    connection = sqlite3.connect("conversations.db")
    cursor = connection.cursor()

    # Eliminar la tabla si ya existe (opcional, si quieres recrearla siempre)
    cursor.execute("DROP TABLE IF EXISTS conversations")

    # Crear la tabla con la estructura correcta
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )

    # Crear índice para mejorar el rendimiento de las búsquedas por perfil
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profile ON conversations(profile)")

    # Insertar múltiples datos de prueba para probar la paginación
    mensajes = [("default", f"Mensaje de prueba número {i}") for i in range(1, 51)]
    cursor.executemany(
        "INSERT INTO conversations (profile, message) VALUES (?, ?)", mensajes
    )

    connection.commit()
    connection.close()
    print("Base de datos inicializada correctamente con 50 mensajes de prueba.")


if __name__ == "__main__":
    initialize_database()
