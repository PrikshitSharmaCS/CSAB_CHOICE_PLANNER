Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  Starting CSAB Choice Filling Assistant..." -ForegroundColor Green
Write-Host "  Opening in browser: http://localhost:8000" -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Cyan

Start-Process "http://localhost:8000"

$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $pythonExe) {
    & $pythonExe (Join-Path $PSScriptRoot "app.py")
} else {
    python (Join-Path $PSScriptRoot "app.py")
}
