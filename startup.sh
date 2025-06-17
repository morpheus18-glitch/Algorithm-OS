#!/usr/bin/env bash
set -e

# Start backend and frontend for local development.
# Backend: FastAPI served by uvicorn on port 8000.
# Frontend: static files served via Python HTTP server on port 8080.

# Install Python dependencies if needed
pip install --quiet -r backend/requirements.txt

# Start backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Serve frontend
cd frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!
cd ..

trap 'kill $BACKEND_PID $FRONTEND_PID' EXIT

wait
