# TradeGPT — Démarrage frontend (Windows PowerShell)
Set-Location "$PSScriptRoot\..\frontend"

Write-Host "Installation des dépendances npm..."
npm install

Write-Host "Démarrage du frontend React sur http://localhost:5173"
npm run dev
