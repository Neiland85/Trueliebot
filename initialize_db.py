import sqlite3

def initialize_database():
    connection = sqlite3.connect("conversations.db")
    cursor = connection.cursor()

    # Eliminar la tabla si ya existe (opcional, si quieres recrearla siempre)
    cursor.execute("DROP TABLE IF EXISTS conversations")

    # Crear la tabla con la estructura correcta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    # Insertar datos de prueba
    cursor.execute("""
        INSERT INTO conversations (profile, message)
        VALUES (?, ?)
    """, ("default", "Hola, esta es una conversación de prueba."))

    connection.commit()
    connection.close()
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    initialize_database()

