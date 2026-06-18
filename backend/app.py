import os
import re
import smtplib
from email.message import EmailMessage

from flask import Flask, request, jsonify, send_from_directory

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


def clean_contact_field(value):
    if not isinstance(value, str):
        return ""
    return value.strip()


def is_valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def send_contact_email(name, sender_email, message):
    recipient = os.environ.get("CONTACT_RECIPIENT_EMAIL", "takudzwajohn3275@gmail.com")
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_from = os.environ.get("SMTP_FROM_EMAIL") or smtp_username

    if not all([smtp_host, smtp_username, smtp_password, smtp_from, recipient]):
        raise RuntimeError("Contact email service is not configured.")

    email = EmailMessage()
    email["Subject"] = f"Portfolio contact message from {name}"
    email["From"] = smtp_from
    email["To"] = recipient
    email["Reply-To"] = sender_email
    email.set_content(
        "\n".join([
            "New message from your portfolio contact form.",
            "",
            f"Name: {name}",
            f"Email: {sender_email}",
            "",
            "Message:",
            message,
        ])
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(email)


@app.route('/contact', methods=['POST'])
def contact():
    payload = request.get_json(silent=True) or {}
    name = clean_contact_field(payload.get("name"))
    sender_email = clean_contact_field(payload.get("email"))
    message = clean_contact_field(payload.get("message"))

    if not name or not sender_email or not message:
        return jsonify({"response": "Name, email, and message are required."}), 400
    if len(name) > 120 or len(sender_email) > 254 or len(message) > 3000:
        return jsonify({"response": "Your message is too long."}), 400
    if not is_valid_email(sender_email):
        return jsonify({"response": "Please enter a valid email address."}), 400

    try:
        send_contact_email(name, sender_email, message)
    except RuntimeError as error:
        app.logger.warning("Contact email configuration error: %s", error)
        return jsonify({"response": "Contact email is not configured yet."}), 503
    except Exception:
        app.logger.exception("Contact email failed")
        return jsonify({"response": "Your message could not be sent right now."}), 502

    return jsonify({"response": "Your message was sent successfully."})


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
