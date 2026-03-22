# Script to install TensorFlow with CUDA support for SRGAN API

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Installing TensorFlow GPU for SRGAN" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$venvPath = "D:\aiie\aiie-srgan-api\venv\Scripts"

Write-Host "`n[1/2] Installing TensorFlow base..." -ForegroundColor Yellow
& "$venvPath\pip.exe" install --default-timeout=300 tensorflow==2.17.0

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install TensorFlow" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/2] Installing CUDA libraries..." -ForegroundColor Yellow
& "$venvPath\pip.exe" install --default-timeout=300 `
    nvidia-cudnn-cu12 `
    nvidia-cublas-cu12 `
    nvidia-cuda-runtime-cu12

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some CUDA libraries may not be installed" -ForegroundColor Yellow
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Testing GPU detection..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

& "$venvPath\python.exe" -c @"
import tensorflow as tf
print('TensorFlow version:', tf.__version__)
gpus = tf.config.list_physical_devices('GPU')
print('GPU devices:', gpus)
if len(gpus) > 0:
    print('✅ GPU detected!')
    for gpu in gpus:
        print(f'   - {gpu}')
else:
    print('⚠️  No GPU detected - running on CPU')
"@

Write-Host "`nInstallation complete!" -ForegroundColor Green
