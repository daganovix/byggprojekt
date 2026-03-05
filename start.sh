#!/usr/bin/env bash
# ── Byggprojekt Sverige – quick start ──────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

echo "=== Byggprojekt Sverige ==="
echo ""

# ── Backend ──────────────────────────────────────────────────────────────────
echo "[1/4] Setting up Python virtual environment…"
cd "$BACKEND"
python3 -m venv .venv
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "[2/4] Seeding database with demo projects…"
python seed.py

echo "[3/4] Starting FastAPI backend on http://localhost:8000 …"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# ── Frontend ─────────────────────────────────────────────────────────────────
echo "[4/4] Installing and starting React frontend on http://localhost:5173 …"
cd "$FRONTEND"
npm install --silent
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✓ App running!"
echo "  Frontend → http://localhost:5173"
echo "  API      → http://localhost:8000/api/projects"
echo "  API docs → http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT INT TERM
wait
