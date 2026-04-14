The Project has been attempted in two ways .One in Grok-Style and other using Ollam model with Streamlit deployment.


# Grok-Style BI Sales Chatbot

This repository is a small Streamlit app that parses a PDF with sales data and provides a conversational "Grok"-style assistant about the data.

Contents:
- `app.py` — Streamlit app entrypoint
- `pdf_reader.py`, `data_analysis.py` — PDF parsing / data summarization helpers
- `grok_style.py` — helper that produces a Grok-style reply (lazily loads models)
- `requirements.txt` — Python dependencies

This README covers how to push the repo to GitHub and deploy to Streamlit Community Cloud.

## Preparation (local)

1. Create and activate a virtualenv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

2. Install lightweight dependencies for development (no heavy ML libs):

```powershell
pip install streamlit pdfplumber pandas
```

3. (Optional) If you plan to load models locally, install CPU PyTorch and transformers:

```powershell
# CPU-only PyTorch wheel; may take time and disk space
pip install --index-url https://download.pytorch.org/whl/cpu torch
pip install transformers
```

Note: installing `torch` and `transformers` may fail on Streamlit Community Cloud or be too large. For production use, prefer a remote inference API.

## GitHub: push your repo

If your local folder is not a git repo yet, run these commands in PowerShell (replace `<your-repo-name>`):

```powershell
# initialize
git init
git add .
git commit -m "Initial commit: Streamlit BI Grok chatbot"
# create a GitHub repo via web UI or use gh (optional)
# If using GitHub web UI: create repo named <your-repo-name> and then:
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git branch -M main
git push -u origin main
```

If you have `gh` installed and authenticated:

```powershell
gh repo create <your-username>/<your-repo-name> --public --source=. --remote=origin --push
```

## Deploy to Streamlit Community Cloud

1. Go to https://streamlit.io/cloud and sign in with your GitHub account.
2. Click **New app** -> choose the repository and branch (e.g. `main`).
3. Set the app path to `app.py` (the entrypoint) and deploy.

Environment variables & secrets
- If you want to set `GROK_MODEL` to a particular model name, add it under App settings -> Advanced -> Environment variables.

Important notes for models
- Do not attempt to load multi-GB models on Streamlit Community Cloud. The app will likely OOM or fail during install. Keep `grok_style.py` default to a small model (like `gpt2`) or use remote inference.
- Recommended: host large models on a model-serving endpoint (Hugging Face Inference API, Replicate, or your own API) and have `grok_reply` call that endpoint.

Troubleshooting
- Build fails because `torch` is too big: remove `torch` and `transformers` from `requirements.txt` (or move them to an optional file) and use remote inference.
- If the app shows `(model unavailable) ...` that means `transformers` or the selected model couldn't load. Use remote inference or set `GROK_MODEL` to a small model.

## Optional improvements I can help with
- Add remote-inference client in `grok_style.py` that calls Hugging Face / Replicate and reads an API key from environment variables.
- Create a `Dockerfile` for containerized deployment on a VM / cloud provider with GPU support.
- Create a small GitHub Actions workflow to run basic tests on push.

If you'd like, tell me which GitHub repo name to create and whether you want me to implement remote inference or add a `Dockerfile`.

---
Created to help you deploy the Streamlit app using GitHub and Streamlit Cloud.
