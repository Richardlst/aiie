# Windows optimized server startup script
# This script configures Windows socket buffers and runs the SD API server

# Ensure we're in the right directory
Set-Location -Path $PSScriptRoot
Set-Location -Path ".."

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "Virtual environment not found!"
    exit 1
}

# Run with Python runner (better Windows socket handling)
Write-Host "Starting SD API server (Windows optimized)..." -ForegroundColor Cyan
python app/run_server.py
