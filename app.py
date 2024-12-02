from flask import Flask, request, jsonify
import re
import os
import openai
from dotenv import load_dotenv
import logging

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


KEYWORDS = {
    "préstamo": 3,
    "dinero": 2,
    "urgente": 2,
    "oferta": 1,
    "gratis": 1,
    "ganar": 1,
}

QUESTIONS = [
    "¿Cómo te describirías a ti mismo en situaciones de conflicto? (a) Evito la confrontación, (b) Busco una solución, (c) Defiendo mi postura firmemente",
    "¿Cómo reaccionas ante la presión social? (a) Me dejo influenciar fácilmente, (b) Evalúo la situación antes de actuar, (c) Me mantengo firme en mis decisiones",
    "¿Confías fácilmente en las personas? (a) Sí, tiendo a confiar en la mayoría de las personas, (b) Confío después de conocerlas un poco, (c) Soy cauteloso y me cuesta confiar",
]

def analyze_conversation(conversation):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=(f"""
                Analiza la siguiente conversación de WhatsApp en busca de posibles señales de engaño o manipulación, 
                como solicitudes de dinero inesperadas, promesas exageradas, inconsistencias, lenguaje 
                manipulador o presión para tomar decisiones rápidas. Responde "positive" si la conversación es 
                potencialmente problemática y "negative" si no detectas nada sospechoso:

                Conversación:
                {conversation}
            """).strip(),
            max_tokens=1,
            n=1,
            stop=None,
            temperature=0.7,
        )

        score = 0
        words = re.findall(r'\b\w+\b', conversation.lower())
        conversation_length = len(words)

        for word, value in KEYWORDS.items():
            word_count = words.count(word)
            score += word_count * value

        if conversation_length > 0:
            score /= conversation_length
            gpt_influence = 0.01
            if response.choices[0].text.strip().lower() == "positive":
                score += gpt_influence

        return score

    except openai.error.OpenAIError as e:
        print(f"Error en la API de OpenAI: {e}")
        return -1

def get_user_profile(answers):
    profile = ""
    a_count = answers.count('a')
    b_count = answers.count('b')
    c_count = answers.count('c')
    if a_count > b_count and a_count > c_count:
      profile = "A"
    elif b_count > a_count and b_count > c_count:
        profile = "B"
    elif c_count > a_count and c_count > b_count:
        profile = "C"
    else: 
        profile = "B"
    return profile

def adapt_response(result, profile):
    if result == "No fiable":
        if profile == "A":
            response = "Ten mucho cuidado.  Habla con alguien de confianza."
        elif profile == "B":
            response = "El análisis indica alto riesgo. Investiga más."
        elif profile == "C":
            response = "¡Mucho cuidado!  Bloquea el contacto."
    elif result == "Posiblemente sospechoso":
        if profile == "A":
            response = "Sé prudente. Podría ser sospechoso."
        elif profile == "B":
            response = "El análisis muestra algunas señales de alerta. "
        elif profile == "C":
            response = "Mantén la cautela."
    else:
        if profile == "A":
            response = "El análisis indica que es fiable. Pero sigue siendo prudente."
        elif profile == "B":
            response = "Parece ser una conversación fiable. "
        elif profile == "C":
            response = "El análisis indica fiabilidad."
    return response

def determine_result(score):
    if score > 0.03:
        result = "No fiable"
    elif score > 0.015:
        result = "Posiblemente sospechoso"
    else:
        result = "Fiable"
    return result

@app.route('/analyze', methods=['POST'])
def analyze_conversation_route():
    conversation = request.json.get('conversation')
    answers = request.json.get('answers')

    logging.info(f"Solicitud recibida: conversación={conversation}, respuestas={answers}")

    score = analyze_conversation(conversation)

    if score == -1:
        logging.error("Error en la API de OpenAI")
        return jsonify({'error': 'Error en la API de OpenAI'}), 500

    result = determine_result(score)
    profile = get_user_profile(answers)
    adapted_response = adapt_response(result, profile)

    logging.info(f"Resultado del análisis: resultado={result}, puntuación={score}, perfil={profile}, respuesta={adapted_response}")

    return jsonify({'result': result, 'score': score, 'profile': profile, 'response': adapted_response, 'questions': QUESTIONS})

if __name__ == '__main__':
    app.run(debug=True)
