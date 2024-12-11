import sqlite3
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/api/ask', methods=['POST'])
def ask_openai():
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({'status': 'error', 'message': 'La pregunta no puede estar vacía.'}), 400

    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            max_tokens=150
        )
        answer = response.choices[0].text.strip()
        return jsonify({'status': 'success', 'answer': answer})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    profile = request.args.get('profile', 'default')

    try:
        connection = sqlite3.connect('conversations.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM conversations WHERE profile = ?", (profile,))
        rows = cursor.fetchall()
        connection.close()

        if rows:
            return jsonify({'status': 'success', 'data': rows})
        else:
            return jsonify({'status': 'error', 'message': 'No se encontraron conversaciones para este perfil.'}), 404
    except sqlite3.Error as e:
        return jsonify({'status': 'error', 'message': f'Error en la base de datos: {str(e)}'}), 500

@app.route('/')
def home():
    return "API de gestión de conversaciones activa."

if __name__ == '__main__':
    app.run(debug=True)

