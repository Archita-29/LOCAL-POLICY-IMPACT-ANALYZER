# Local Policy Impact Analyzer - Quick Dev Runner
Write-Host "Starting Local Policy Impact Analyzer..." -ForegroundColor Cyan

# 1. Start FastAPI Backend in a separate window
$backend = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='backend'; .venv\Scripts\python -m uvicorn app.main:app --port 8000 --reload" -PassThru
Write-Host "[OK] Backend running at http://localhost:8000 (PID: $($backend.Id))" -ForegroundColor Green

# 2. Start React + Vite Frontend in a separate window
$frontend = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "npm --prefix frontend run dev -- --port 3000" -PassThru
Write-Host "[OK] Frontend running at http://localhost:3000 (PID: $($frontend.Id))" -ForegroundColor Green

# 3. Open browser preview
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host "`nReady! App: http://localhost:3000 | Swagger Docs: http://localhost:8000/docs" -ForegroundColor Yellow
