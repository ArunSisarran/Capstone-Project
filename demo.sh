#!/bin/sh
# Starts vision (:8001), backend (:8000) and frontend (:5173); Ctrl-C stops all. -Arun
cd "$(dirname "$0")"
export SSL_CERT_FILE="$(venv/bin/python -m certifi)"  # macOS python.org Python has no CA certs -Arun
trap 'kill 0' EXIT
(cd VisionModel && ../venv/bin/python serve.py --port 8001) &
(cd backend && ../venv/bin/uvicorn app.main:app --port 8000) &
(cd frontend && npm run dev) &
wait
