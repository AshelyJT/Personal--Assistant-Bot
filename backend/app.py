from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys

# Allow import from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from nlp_bot import AdvancedPersonalAssistant

# Setup Flask with correct template folder paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = base_dir
static_dir = os.path.join(base_dir, 'frontend')
profile_dir = os.path.join(base_dir, 'profile')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize Bot
bot = AdvancedPersonalAssistant()

@app.route('/')
def home():
    return render_template('profile/index.html',
                         personal_info=bot.data.get('personal_info', {}),
                         metrics=bot.get_profile_metrics(),
                         public_links=bot.get_public_links(),
                         welcome_message="Hello! I am Takudzwa's interactive resume. Ask me about my Python projects or my time at OK Zimbabwe.")

@app.route('/profile-assets/<path:filename>')
def profile_asset(filename):
    return send_from_directory(profile_dir, filename)

@app.route('/resume')
def resume():
    return send_from_directory(
        profile_dir,
        'Takudzwa John CV.pdf',
        as_attachment=True,
        download_name='Takudzwa-Ashely-John-CV.pdf',
    )

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
