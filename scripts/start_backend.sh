#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

if [ ! -d "backend/.venv" ]; then
    echo "Création du virtualenv Python..."
    python3 -m venv backend/.venv
fi

echo "Activation du virtualenv..."
source backend/.venv/bin/activate

echo "Installation des dépendances..."
pip install -r backend/requirements.txt --quiet

if [ ! -f ".env" ]; then
    echo "Copie de .env.example vers .env..."
    cp .env.example .env
fi

echo "Démarrage du backend FastAPI sur http://localhost:8000"
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
