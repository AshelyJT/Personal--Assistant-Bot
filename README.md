# Portfolio and Personal Assistant

A Flask-powered personal portfolio with an integrated resume chatbot for answering questions about skills, experience, education, projects, contact details, and interview-style examples.

## Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r backend\requirements.txt
python -m spacy download en_core_web_sm
```

For better semantic matching, you can also install the medium spaCy model:

```powershell
python -m spacy download en_core_web_md
```

## Run

```powershell
python backend\run.py
```

Open `http://127.0.0.1:5000` in your browser.

The static portfolio lives in `frontend/`. The Python assistant and all Python
dependencies live in `backend/`.

## Deploy

This project needs a Python web service because Flask serves the portfolio,
profile assets, downloadable CV, and the `/chat` API. Netlify can build Python
dependencies, but it does not run
`python backend/run.py` as a persistent web server.

The repository includes a Render Blueprint in `render.yaml`. It configures
Render to use `backend` as the service root, install the backend requirements,
and use Python 3.11. To deploy:

1. Push the repository to GitHub.
2. In Render, create or sync the Blueprint from the repository.
3. Render installs `backend/requirements.txt` and starts the app with:

```text
gunicorn run:app
```

For an existing manually configured Render service, set **Root Directory** to
`backend`. Keep the build command as `pip install -r requirements.txt` and the
start command as `gunicorn run:app`.

Locally, continue using `python backend\run.py`. In production, Gunicorn imports
the Flask application named `app` from `backend/run.py`.

## Test

```powershell
python -m unittest discover
```

## Profile Data

The portfolio source and assets live in `frontend/`. Assistant knowledge lives
in `backend/data.json`; keep it aligned with visible portfolio projects and
contact details. Placeholder links are intentionally hidden from assistant
responses.

## Example Questions

- What are your skills?
- Tell me about your experience.
- Show me your projects.
- What is your education background?
- How can I contact you?
- Tell me about yourself.
