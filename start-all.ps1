# AIIE Project - Start All Services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AIIE Project - Start All Services   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
docker ps 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop!" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Docker is running" -ForegroundColor Green

# Check and start PostgreSQL
Write-Host "`n[2/5] Checking PostgreSQL..." -ForegroundColor Yellow
$postgresRunning = docker ps --filter "name=aiie-postgres" --format "{{.Names}}"
if ($postgresRunning -ne "aiie-postgres") {
    # Check if container exists but is stopped
    $postgresExists = docker ps -a --filter "name=aiie-postgres" --format "{{.Names}}"
    if ($postgresExists -eq "aiie-postgres") {
        Write-Host "Starting existing PostgreSQL container..." -ForegroundColor Yellow
        docker start aiie-postgres
    } else {
        Write-Host "Creating new PostgreSQL container..." -ForegroundColor Yellow
        docker run -d `
            --name aiie-postgres `
            -e POSTGRES_DB=aiie_db `
            -e POSTGRES_USER=postgres `
            -e POSTGRES_PASSWORD=postgres `
            -p 5433:5432 `
            postgres:15
    }
    Start-Sleep -Seconds 5
}
Write-Host "OK: PostgreSQL is running" -ForegroundColor Green

# Check and start MinIO
Write-Host "`n[3/5] Checking MinIO..." -ForegroundColor Yellow
$minioRunning = docker ps --filter "name=aiie-minio" --format "{{.Names}}"
if ($minioRunning -ne "aiie-minio") {
    # Check if container exists but is stopped
    $minioExists = docker ps -a --filter "name=aiie-minio" --format "{{.Names}}"
    if ($minioExists -eq "aiie-minio") {
        Write-Host "Starting existing MinIO container..." -ForegroundColor Yellow
        docker start aiie-minio
    } else {
        Write-Host "Creating new MinIO container..." -ForegroundColor Yellow
        docker run -d `
            --name aiie-minio `
            -p 9000:9000 `
            -p 9001:9001 `
            -e MINIO_ROOT_USER=minioadmin `
            -e MINIO_ROOT_PASSWORD=minioadmin `
            minio/minio server /data --console-address ":9001"
        Write-Host "NOTE: Visit http://localhost:9001 to create bucket 'aiie-storage'" -ForegroundColor Yellow
    }
    Start-Sleep -Seconds 3
}
Write-Host "OK: MinIO is running" -ForegroundColor Green

# Start Agent API
Write-Host "`n[4/5] Starting Agent API (Backend)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\aiie-agent-api'; .\venv\Scripts\activate; Write-Host 'Agent API running on http://localhost:8000' -ForegroundColor Green; uvicorn app.main:app --reload --port 8000"

# Start SD API
Write-Host "Starting Stable Diffusion API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\aiie-sd-api'; `$env:PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'; .\venv\Scripts\activate; Write-Host 'SD API running on http://localhost:8001' -ForegroundColor Green; uvicorn app.main:app --reload --port 8001"

# Start SRGAN API
Write-Host "Starting SRGAN API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\aiie-srgan-api'; Write-Host 'SRGAN API running on http://localhost:8002' -ForegroundColor Green; .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8002"

# Wait for APIs to start
Write-Host "`nWaiting for APIs to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Start Frontend
Write-Host "`n[5/5] Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\aiie-ui'; Write-Host 'Frontend is running...' -ForegroundColor Green; npm run dev"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "All services started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  - Frontend:     http://localhost:5173" -ForegroundColor White
Write-Host "  - Agent API:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - SD API:       http://localhost:8001/docs" -ForegroundColor White
Write-Host "  - SRGAN API:    http://localhost:8002/docs" -ForegroundColor White
Write-Host "  - MinIO:        http://localhost:9001" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT NOTES:" -ForegroundColor Yellow
Write-Host "  1. First run of SD API will download model (~4GB)" -ForegroundColor Yellow
Write-Host "  2. Remember to create bucket 'aiie-storage' in MinIO" -ForegroundColor Yellow
Write-Host "  3. Configure OPENAI_API_KEY in aiie-agent-api\.env" -ForegroundColor Yellow
Write-Host ""
