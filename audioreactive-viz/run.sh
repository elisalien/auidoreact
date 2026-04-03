#!/usr/bin/env bash
# ─── Audioreactive Visualizer — Launch Script ───
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"

# Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "[Setup] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate
source "$VENV_DIR/bin/activate"

# Install / update deps
echo "[Setup] Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Launch
echo "[Launch] Starting visualizer..."
python main.py "$@"
