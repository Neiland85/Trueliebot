import sqlite3


def initialize_database():
    connection = sqlite3.connect("conversations.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation TEXT NOT NULL,
            answers TEXT NOT NULL,
            score INTEGER NOT NULL,
            result TEXT NOT NULL,
            profile TEXT NOT NULL,
            response TEXT NOT NULL
        )
    """
    )

    cursor.execute("SELECT COUNT(*) FROM conversations")
    if cursor.fetchone()[0] == 0:
        initial_data = [
            (
                "¿Cómo estás?",
                "Estoy bien, gracias.",
                10,
                "positivo",
                "default",
                "Esta es una respuesta de prueba.",
            ),
            (
                "¿Qué puedes hacer?",
                "Puedo ayudarte con tareas básicas.",
                8,
                "informativo",
                "default",
                "Soy un bot y aquí para asistirte.",
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO conversations (conversation, answers, score, result, profile, response)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            initial_data,
        )
        print("Datos iniciales insertados en la tabla 'conversations'.")

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
