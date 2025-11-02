run-backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	streamlit run frontend/streamlit_app.py

docker-up:
	docker compose up --build

lint:
	python -m compileall .
