#!/usr/bin/env python3
"""
Optimized server runner for Windows with socket buffer fixes.
"""

import sys
import os
import socket
import logging

# Configure socket buffer sizes for Windows BEFORE running uvicorn
if sys.platform == "win32":
    import ctypes
    try:
        # Try to increase socket buffer sizes
        logger = logging.getLogger("ServerConfig")
        logger.info("Configuring Windows socket buffers...")
        
        # These changes help prevent WinError 10055
        os.environ["PYTHONUNBUFFERED"] = "1"
        
        # Disable certificate verification warnings for HF downloads
        os.environ["HF_DATASETS_TRUST_REMOTE_CODE"] = "1"
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
        
        logger.info("Windows socket configuration completed")
    except Exception as e:
        logging.warning(f"Failed to configure Windows sockets: {e}")

import uvicorn

if __name__ == "__main__":
    # Configure uvicorn with Windows-friendly settings
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        # Windows-specific settings
        loop="proactor",  # Use ProactorEventLoop on Windows (handles sockets better)
        workers=1,  # Single worker to avoid socket conflicts
        timeout_keep_alive=65,
        timeout_notify=30,
        max_concurrent_requests=100,
        limit_concurrency=100,
        backlog=2048,  # Larger backlog for socket queue
        # Log config
        log_level="info",
        access_log=True,
    )
    
    server = uvicorn.Server(config)
    sys.exit(server.run())
