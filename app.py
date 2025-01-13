from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Configuración de la base de datos
DB_NAME = "conversations.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint raíz para verificar el estado de la API
@app.route('/', methods=['GET'])
def home():
    return "API de gestión de conversaciones activa.", 200

# Endpoint GET /api/conversations
@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    try:
        profile = request.args.get('profile', 'default')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE profile = ?", (profile,))
        conversations = cursor.fetchall()
        conn.close()

        if not conversations:
            return jsonify({"message": "No conversations found"}), 404
        
        data = [{"id": row["id"], "profile": row["profile"], "message": row["message"]} for row in conversations]
        return jsonify({"data": data, "status": "success"}), 200
    except Exception as e:
        app.logger.error(f"Error in GET /api/conversations: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

# Endpoint POST /api/conversations
@app.route('/api/conversations', methods=['POST'])
def post_conversations():
    try:
        data = request.get_json()
        profile = data.get("profile")
        message = data.get("message")

        if not profile or not message:
            return jsonify({"error": "Invalid data"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO conversations (profile, message) VALUES (?, ?)", (profile, message))
        conn.commit()
        conn.close()

        return jsonify({"message": "Conversation created"}), 201
    except Exception as e:
        app.logger.error(f"Error in POST /api/conversations: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True)

