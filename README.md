# Portfolio and Personal Assistant

A Flask-powered personal portfolio with an integrated resume chatbot for answering questions about skills, experience, education, projects, contact details, and interview-style examples.

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

The portfolio is the main page. Use any **Ask My Assistant** button to open the
chat drawer without leaving the portfolio.

## Deploy

This project needs a Python web service because Flask serves the portfolio,
profile assets, downloadable CV, and the `/chat` API. Netlify can build Python
dependencies, but it does not run
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

The portfolio source and assets live in `profile/`. Assistant knowledge lives in
`data.json`; keep it aligned with visible portfolio projects and contact details.
Placeholder links are intentionally hidden from assistant responses.

## Example Questions

- What are your skills?
- Tell me about your experience.
- Show me your projects.
- What is your education background?
- How can I contact you?
- Tell me about yourself.
