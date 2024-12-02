from flask import Flask, request, jsonify

app = Flask(__name__)

KEYWORDS = {
    "préstamo": 3,
    "dinero": 2,
    "urgente": 2,
    "oferta": 1,
    "gratis": 1,
    "ganar": 1,
}

def analyze_conversation(conversation):
    score = 0
    for word, value in KEYWORDS.items():
        if word in conversation.lower(): 
            score += value
    return score

@app.route('/analyze', methods=['POST'])
def analyze_conversation_route():
    conversation = request.json.get('conversation')
    score = analyze_conversation(conversation)
    # Lógica simple de evaluación (ajusta los umbrales)
    if score > 5:
        result = "No fiable"
    elif score > 2:
        result = "Posiblemente sospechoso"
    else:
        result = "Fiable"
    return jsonify({'result': result, 'score': score})

if __name__ == '__main__':
    app.run(debug=True)
