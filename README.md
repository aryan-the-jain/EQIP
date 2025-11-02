# Eqip.ai Starter (Streamlit + FastAPI + Agents)

A minimal, production-leaning scaffold for the Eqip.ai IP consultancy agent.

## Quickstart (dev)
```bash
# 1) Local virtualenv (optional) or use Docker
pip install -r requirements.txt

# 2) Start backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 3) Start Streamlit frontend
streamlit run frontend/streamlit_app.py
```

## With Docker
```bash
docker compose up --build
```

## Env
Copy `.env.example` → `.env` and adjust values.
