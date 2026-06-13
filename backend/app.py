from flask import Flask, request, jsonify, send_from_directory
import os

try:
    from .nlp_bot import AdvancedPersonalAssistant
except ImportError:
    from nlp_bot import AdvancedPersonalAssistant

backend_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(backend_dir)
frontend_dir = os.path.join(project_dir, "frontend")

app = Flask(__name__, static_folder=frontend_dir, static_url_path="")

# Initialize Bot
bot = AdvancedPersonalAssistant()


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route('/')
def home():
    return send_from_directory(frontend_dir, "index.html")


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/chat', methods=['POST'])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get('message', '')

    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({'response': 'Please enter a message so I can help.'}), 400

    answer = bot.get_answer(user_message)
    if answer.get('intent') == 'fallback':
        app.logger.info("Fallback question: %s", user_message)

    return jsonify(answer)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
