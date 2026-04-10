PAUSED on 2025-11-20

Reason: Pausing this project to focus on other work.

Status summary:
- Streamlit app updated to avoid loading large models locally.
- `grok_style.py` supports remote inference via `HF_API_TOKEN` and `GROK_API_URL`.
- Added `requirements_streamlit.txt` to keep Streamlit Cloud installs lightweight.

How to resume:
1. Restore environment: create/activate `.venv` and install dependencies.
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
   - `pip install -r requirements_streamlit.txt`
2. If using remote inference, set `HF_API_TOKEN` in your environment or Streamlit Cloud app secrets.
3. Run Streamlit: `streamlit run app.py`

Notes:
- If you plan to run large models locally, install `torch` and `transformers` separately.
- This pause snapshot includes `requirements-paused.txt` and `PYTHON_VERSION.txt` files.
