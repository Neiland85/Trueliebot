from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_conversation():
    conversation = request.json.get('conversation')
    result = "En desarrollo..."
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
