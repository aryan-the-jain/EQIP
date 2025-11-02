# EQIP - Equitable IP Collaboration Assistant

A comprehensive AI-powered platform for intellectual property analysis, contract generation, and collaborative IP management.

## Features

- **AI-Powered IP Analysis**: Advanced agents for contribution attribution, ownership arrangement, and IP path finding
- **Contract Generation**: Automated contract drafting and composition
- **Interactive Web Interface**: Modern Streamlit-based frontend with enhanced UI/UX
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Database Integration**: SQLite database with proper schema management
- **RAG System**: Knowledge base integration with embedding services
- **Docker Support**: Full containerization for easy deployment

## Quickstart (Development)

```bash
# 1) Install dependencies
pip install -r requirements.txt

# 2) Start backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 3) Start Streamlit frontend
streamlit run frontend/streamlit_app_enhanced.py
```

## With Docker

```bash
docker compose up --build
```

## Service Management

Use the provided scripts for service management:

```bash
# Check service health
./check_services.sh

# Restart services
./restart_services.sh

# Stop services
./stop_services.sh
```

## Environment Setup

Copy `.env.example` → `.env` and adjust values for your environment.

## Testing

Run the comprehensive test suite:

```bash
python test_pipeline.py
python test_rag.py
```
