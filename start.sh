#!/bin/bash
set -e

BACKEND_PID=0
FRONTEND_PID=0

cleanup() {
  if [[ $BACKEND_PID -ne 0 ]]; then
    kill $BACKEND_PID 2>/dev/null || true
  fi
  if [[ $FRONTEND_PID -ne 0 ]]; then
    kill $FRONTEND_PID 2>/dev/null || true
  fi
  exit 0
}

trap cleanup INT TERM

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

(cd frontend && python3 -m http.server 8080) &
FRONTEND_PID=$!

wait $BACKEND_PID $FRONTEND_PID
