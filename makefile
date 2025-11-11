.PHONY: setup ingest index app all


setup:
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && cp -n .env.example .env || true


ingest:
python scripts/rebuild_index.py


app:
python -m src.rag.app


all: ingest app