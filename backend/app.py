from flask import Flask, render_template, request, jsonify
import os
import sys

# Allow import from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from nlp_bot import AdvancedPersonalAssistant

# Setup Flask with correct template folder paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(base_dir, 'frontend')
static_dir = os.path.join(base_dir, 'frontend')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize Bot
bot = AdvancedPersonalAssistant()

@app.route('/')
def home():
    return render_template('index.html', 
                         personal_info=bot.data.get('personal_info', {}),
                         welcome_message="Hello! I am Takudzwa's interactive resume. Ask me about my Python projects or my time at OK Zimbabwe.")

@app.route('/chat', methods=['POST'])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get('message', '')

    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({'response': 'Please enter a message so I can help.'}), 400

    response = bot.get_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
