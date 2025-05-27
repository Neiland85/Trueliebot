"""
Script para inicializar la tabla de usuarios en la base de datos.

Este script crea la tabla de usuarios si no existe y añade usuarios de prueba.
"""

import os
import sqlite3
import sys

from models.user import hash_password


def init_users_table() -> None:
    """
    Inicializa la tabla de usuarios.
    """
    # Obtener la ruta de la base de datos
    db_path = os.path.join(os.path.dirname(__file__), "trueliebot_sophisticated.db")

    if not os.path.exists(db_path):
        print(f"Error: Base de datos {db_path} no encontrada.")
        print("Por favor, ejecuta primero initialize_sophisticated_db.py")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Crear tabla de usuarios
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'user',
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Verificar si ya existen usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            print("Creando usuarios de prueba...")

            # Crear usuario normal
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, email, password_hash, rol, activo)
                VALUES (?, ?, ?, ?, 1)
            """,
                (
                    "Usuario Demo",
                    "demo@trueliebot.com",
                    hash_password("trueliebot-demo"),
                    "user",
                ),
            )

            # Crear usuario administrador
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, email, password_hash, rol, activo)
                VALUES (?, ?, ?, ?, 1)
            """,
                (
                    "Admin Demo",
                    "admin@trueliebot.com",
                    hash_password("trueliebot-admin-demo"),
                    "admin",
                ),
            )

            conn.commit()
            print("Usuarios de prueba creados correctamente.")
        else:
            print(f"Ya existen {user_count} usuarios en la base de datos.")

    except Exception as e:
        conn.rollback()
        print(f"Error al inicializar la tabla de usuarios: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    print("Inicializando tabla de usuarios...")
    init_users_table()
    print("¡Tabla de usuarios inicializada correctamente!")
