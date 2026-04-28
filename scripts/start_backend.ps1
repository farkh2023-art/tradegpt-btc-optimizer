# TradeGPT — Démarrage backend (Windows PowerShell)
Set-Location "$PSScriptRoot\.."

if (-not (Test-Path "backend\.venv")) {
    Write-Host "Création du virtualenv Python..."
    python -m venv backend\.venv
}

Write-Host "Activation du virtualenv..."
& "backend\.venv\Scripts\Activate.ps1"

Write-Host "Installation des dépendances..."
pip install -r backend/requirements.txt --quiet

if (-not (Test-Path ".env")) {
    Write-Host "Copie de .env.example vers .env..."
    Copy-Item ".env.example" ".env"
}

Write-Host "Démarrage du backend FastAPI sur http://localhost:8000"
Set-Location backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
