# TradeGPT — Démarrage complet (backend + frontend en parallèle)
$root = Split-Path $PSScriptRoot

Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start_backend.ps1" -WindowStyle Normal
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start_frontend.ps1" -WindowStyle Normal

Write-Host "Backend : http://localhost:8000"
Write-Host "Frontend : http://localhost:5173"
Write-Host "API docs : http://localhost:8000/docs"
