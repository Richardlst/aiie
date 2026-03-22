# Script dừng tất cả services cho dự án AIIE

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AIIE Project - Stop All Services    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Dừng các process Python (uvicorn)
Write-Host "[1/2] Dừng các API services..." -ForegroundColor Yellow
$uvicornProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" }
if ($uvicornProcesses) {
    $uvicornProcesses | Stop-Process -Force
    Write-Host "✅ Đã dừng các API services" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Không tìm thấy API services đang chạy" -ForegroundColor Gray
}

# Dừng Node.js (Vite)
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    $nodeProcesses | Stop-Process -Force
    Write-Host "✅ Đã dừng Frontend" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Không tìm thấy Frontend đang chạy" -ForegroundColor Gray
}

# Tùy chọn: Dừng Docker containers
Write-Host "`n[2/2] Dừng Docker containers..." -ForegroundColor Yellow
$response = Read-Host "Ban co muon dung PostgreSQL va MinIO containers? (y/n)"

if ($response -eq "y" -or $response -eq "Y") {
    docker stop aiie-postgres aiie-minio 2>$null
    Write-Host "✅ Đã dừng Docker containers" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Giữ Docker containers chạy" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ Đã dừng tất cả services!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
