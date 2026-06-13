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

## Deploy

This project needs a Python web service because Flask serves both the website and
the `/chat` API. Netlify can build Python dependencies, but it does not run
`python run.py` as a persistent web server.

The repository includes a Render Blueprint in `render.yaml`. To deploy:

1. Push the repository to GitHub.
2. In Render, create a new Blueprint and select the repository.
3. Render installs `requirements.txt` and starts the app with:

```text
gunicorn run:app
```

Locally, continue using `python run.py`. In production, Gunicorn imports the
Flask application named `app` from `run.py` and listens on Render's assigned
port.

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
