#!/usr/bin/env bash
# ================================================================
# Kharat E-Commerce — Startup Script
# Runs the FastAPI backend server. Open frontend HTML files in your
# browser directly (no extra server needed for the frontend).
# ================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
VENV_DIR="$BACKEND_DIR/.venv"

echo ""
echo "  ⚙  KHARAT — Precision Engineering E-Commerce"
echo "  ─────────────────────────────────────────────"
echo ""

# ── Create virtualenv if it doesn't exist ──────────────────────
if [ ! -d "$VENV_DIR" ]; then
  echo "  [1/3] Creating Python virtual environment..."
  python3 -m venv "$VENV_DIR"
  echo "        ✓ Virtual environment created at backend/.venv"
else
  echo "  [1/3] Virtual environment already exists — skipping."
fi

# ── Install dependencies ───────────────────────────────────────
echo "  [2/3] Installing Python dependencies..."
"$VENV_DIR/bin/pip" install -q -r "$BACKEND_DIR/requirements.txt"
echo "        ✓ Dependencies installed."

# ── Launch Uvicorn ─────────────────────────────────────────────
echo "  [3/3] Starting FastAPI backend server..."
echo ""
echo "  ┌─────────────────────────────────────────────────────┐"
echo "  │  Backend API  →  http://localhost:8000              │"
echo "  │  API Docs     →  http://localhost:8000/docs         │"
echo "  │  Frontend     →  open frontend/index.html           │"
echo "  │                                                     │"
echo "  │  Default Admin Login:                               │"
echo "  │    Email:     admin@kharat.pk                       │"
echo "  │    Password:  admin123                              │"
echo "  └─────────────────────────────────────────────────────┘"
echo ""
echo "  Press Ctrl+C to stop the server."
echo ""

cd "$BACKEND_DIR"
"$VENV_DIR/bin/uvicorn" main:app --reload --host 0.0.0.0 --port 8000
