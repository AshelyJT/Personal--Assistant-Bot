# Personal Assistant Bot

A Flask-based interactive resume chatbot for answering questions about skills, experience, education, projects, contact details, and interview-style examples.

## Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

For better semantic matching, you can also install the medium spaCy model:

```powershell
python -m spacy download en_core_web_md
```

## Run

```powershell
python run.py
```

Open `http://127.0.0.1:5000` in your browser.

## Test

```powershell
python -m unittest discover
```

## Profile Data

Update `data.json` with your real LinkedIn, GitHub, portfolio, resume, and project links before sharing the bot publicly. Placeholder links are intentionally hidden from the app's public link sections.

## Example Questions

- What are your skills?
- Tell me about your experience.
- Show me your projects.
- What is your education background?
- How can I contact you?
- Tell me about yourself.
