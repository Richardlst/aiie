"""
HTTP client utilities with retry logic and connection pooling for calling external APIs.
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Global session for connection pooling
_global_session: Optional[aiohttp.ClientSession] = None


async def get_http_session() -> aiohttp.ClientSession:
    """Get or create a persistent aiohttp session with proper configuration."""
    global _global_session
    
    if _global_session is None or _global_session.closed:
        # Configure timeouts separately - increased for long-running tasks like colorization
        timeout = aiohttp.ClientTimeout(
            total=None,  # No total timeout
            connect=30,   # 30 seconds to connect
            sock_connect=30,  # 30 seconds socket connect
            sock_read=300,  # 5 minutes to read data (colorization can be slow)
        )
        
        # Configure connector with TCP keepalive
        connector = aiohttp.TCPConnector(
            limit=100,  # Max connections
            limit_per_host=10,  # Max connections per host
            ttl_dns_cache=300,  # 5 minutes DNS cache
            enable_cleanup_closed=True,
            keepalive_timeout=30,  # TCP keepalive timeout
        )
        
        _global_session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "Connection": "keep-alive",
            }
        )
        logger.info("Created global HTTP session with connection pooling (5min read timeout)")
    
    return _global_session


async def close_http_session():
    """Close the global HTTP session."""
    global _global_session
    if _global_session and not _global_session.closed:
        await _global_session.close()
        _global_session = None
        logger.info("Closed global HTTP session")


async def make_request_with_retry(
    method: str,
    url: str,
    json_data: Optional[Dict[Any, Any]] = None,
    max_retries: int = 5,  # Increased from 3 to 5
    backoff_factor: float = 3.0,  # Increased from 2.0 to 3.0
    **kwargs
) -> Dict[Any, Any]:
    """
    Make an HTTP request with automatic retry logic.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full URL to request
        json_data: JSON data to send in body
        max_retries: Maximum number of retry attempts (default 5)
        backoff_factor: Exponential backoff multiplier (default 3.0)
        **kwargs: Additional arguments to pass to session request
    
    Returns:
        Response JSON data
    
    Raises:
        HTTPException-like errors on failure
    """
    
    for attempt in range(max_retries):
        try:
            session = await get_http_session()
            
            logger.debug(f"API {method} request attempt {attempt + 1}/{max_retries} to {url}")
            
            async with session.request(
                method,
                url,
                json=json_data,
                ssl=False,
                **kwargs
            ) as response:
                if response.status == 200:
                    logger.debug(f"API request succeeded on attempt {attempt + 1}")
                    return await response.json()
                else:
                    error_text = await response.text()
                    if response.status >= 500 and attempt < max_retries - 1:
                        # Server error, retry
                        wait_time = backoff_factor ** attempt
                        logger.warning(
                            f"API returned {response.status}, retrying in {wait_time}s: {error_text[:200]}"
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(
                            f"API returned {response.status}: {error_text[:500]}"
                        )
        
        except (aiohttp.ClientOSError, aiohttp.ClientConnectionError) as e:
            # Connection errors - retry with backoff
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    f"Connection error on attempt {attempt + 1}/{max_retries}, retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.error(f"Connection failed after {max_retries} attempts: {e}")
                raise RuntimeError(f"Could not connect to service: {str(e)}")
        
        except asyncio.TimeoutError as e:
            # Timeout - retry with longer wait
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    f"Request timeout on attempt {attempt + 1}/{max_retries}, retrying in {wait_time}s"
                )
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.error(f"Request timeout after {max_retries} attempts")
                raise TimeoutError("Service took too long to respond")
        
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}", exc_info=True)
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                await asyncio.sleep(wait_time)
                continue
            raise RuntimeError(f"Error making request: {str(e)}")
    
    raise RuntimeError("Request failed after multiple attempts")


async def post_json(
    url: str,
    data: Dict[Any, Any],
    max_retries: int = 3,
    **kwargs
) -> Dict[Any, Any]:
    """Make a POST request with JSON data and retry logic."""
    return await make_request_with_retry("POST", url, json_data=data, max_retries=max_retries, **kwargs)


async def get_json(
    url: str,
    max_retries: int = 3,
    **kwargs
) -> Dict[Any, Any]:
    """Make a GET request and retry logic."""
    return await make_request_with_retry("GET", url, max_retries=max_retries, **kwargs)
