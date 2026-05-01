# Windows Socket Buffer Fixes for SD API

## Problem
The application was experiencing **WinError 10055** ("An operation on a socket could not be performed because the system lacked sufficient buffer space or because a queue was full") when:
- Downloading large ML models from Hugging Face Hub
- Processing large images during colorization
- Handling concurrent requests

## Root Causes
1. **Large model downloads** - SDXL and Lightning models are several GB each
2. **Windows socket buffer limits** - Default Windows socket buffers are smaller than Linux
3. **No retry logic** - Downloads that fail weren't retried
4. **Uvicorn default settings** - Not optimized for Windows
5. **Blocking downloads in async context** - Could cause timeouts and cancellations

## Solutions Applied

### 1. Download Retry Logic (`colorize.py`)
Added `_download_with_retry()` function with:
- Exponential backoff (2, 4, 8 second waits)
- Specific handling for WinError 10055
- Connection timeout recovery
- Max 3 retry attempts

### 2. HuggingFace Hub Configuration
Set environment variables for better downloads:
```python
HF_HUB_DOWNLOAD_TIMEOUT = "300"  # 5 minutes per chunk
HF_HUB_ETAG_TIMEOUT = "60"       # 1 minute for metadata
HF_HUB_CHUNK_TIMEOUT = "60"      # 1 minute per chunk
```

### 3. Windows Socket Configuration (`main.py`)
- Added ProactorEventLoop detection for Windows
- Increased socket buffer hints
- Proper environment configuration

### 4. Optimized Uvicorn Server
Created `run_server.py` with:
- ProactorEventLoop for Windows sockets
- Single worker to avoid conflicts
- Larger backlog (2048)
- Better timeout settings

### 5. Error Handling
Added proper exception handling for:
- `asyncio.CancelledError` during downloads
- Socket timeout errors
- Connection reset errors

## How to Use

### Option 1: Use Windows-Optimized Runner (Recommended)
```powershell
cd aiie-sd-api
.\scripts\run-windows.ps1
```

### Option 2: Manual with Modified Settings
```bash
python -c "from app.run_server import *; " app.main:app
```

### Option 3: Regular Uvicorn (with manual buffer config)
```bash
# First run to download models (may take longer first time)
uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 1
```

## Performance Tips
1. **First startup takes longer** - Models are downloaded and cached (~15-30 minutes depending on connection)
2. **Subsequent requests are faster** - Models stay in cache
3. **Disable reload in production** - Use `--reload` only during development
4. **Monitor VRAM** - Keep an eye on GPU memory usage with `nvidia-smi` (if using CUDA)

## Troubleshooting

### Still getting WinError 10055?
1. Check internet connection stability
2. Disable antivirus scanning temporarily
3. Reduce concurrent requests
4. Increase timeout values in `settings.py`

### Models taking forever to download?
1. Check HuggingFace status: https://huggingface.co/
2. Try using a VPN if connection is geo-throttled
3. Pre-download models manually from HuggingFace Web UI

### Out of Memory errors?
- Reduce image resolution
- Don't process multiple images concurrently
- Use `enable_model_cpu_offload()` (already enabled)

## Files Modified
- `app/main.py` - Added socket buffer config and error handling
- `app/settings.py` - Added HF Hub environment configuration
- `app/service/colorize.py` - Added retry logic for downloads
- `app/run_server.py` - New optimized uvicorn runner
- `scripts/run-windows.ps1` - New Windows launcher script

## References
- Windows Socket Errors: https://docs.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes
- HuggingFace Hub Config: https://huggingface.co/docs/hub/security-tokens
- ProactorEventLoop: https://docs.python.org/3/library/asyncio.html#platform-support
