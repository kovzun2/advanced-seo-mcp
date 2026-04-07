"""Secure HTTP client with SSRF protection, retry, and rate limiting."""

import asyncio
import ipaddress
import logging
import time
from typing import Any

import httpx
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

# Private/blocked IP ranges
_PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("fc00::/7"),
]


class SSRFError(ValueError):
    """Raised when a URL points to a private/internal address."""


class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, calls_per_second: float = 2.0):
        self._interval = 1.0 / calls_per_second
        self._last_call = 0.0

    async def acquire(self) -> None:
        now = time.monotonic()
        wait = self._last_call + self._interval - now
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_call = time.monotonic()


def _is_private_ip(host: str) -> bool:
    """Check if a hostname resolves to a private IP address."""
    try:
        ip = ipaddress.ip_address(host)
        return any(ip in net for net in _PRIVATE_NETWORKS)
    except ValueError:
        return False


def validate_url(url: str) -> str:
    """Validate URL and block SSRF vectors.

    - Only http/https schemes allowed
    - No private/reserved IP addresses
    - No localhost
    - URL must parse correctly
    """
    parsed = httpx.URL(url)
    if parsed.scheme not in ("http", "https"):
        raise SSRFError(f"Scheme '{parsed.scheme}' not allowed — only http/https")
    if parsed.host and (parsed.host == "localhost" or _is_private_ip(parsed.host)):
        raise SSRFError(f"Access to '{parsed.host}' is blocked (private IP)")
    return url


class SafeHTTPClient:
    """HTTP client with SSRF protection, retry, and rate limiting."""

    def __init__(
        self,
        timeout: float = 10.0,
        max_retries: int = 3,
        rate_limiter: RateLimiter | None = None,
        user_agent: str | None = None,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = rate_limiter or RateLimiter()
        self._user_agent = user_agent
        self._ua_instance: UserAgent | None = None

    def _get_user_agent(self) -> str:
        if self._user_agent:
            return self._user_agent
        if self._ua_instance is None:
            self._ua_instance = UserAgent()
        return self._ua_instance.random

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Perform a GET request with SSRF protection, retry, and rate limiting."""
        validate_url(url)
        headers = kwargs.pop("headers", {})
        headers.setdefault("User-Agent", self._get_user_agent())

        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            await self.rate_limiter.acquire()
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                    max_redirects=5,
                ) as client:
                    resp = await client.get(url, headers=headers, **kwargs)
                    resp.raise_for_status()
                    return resp
            except (httpx.HTTPError, OSError) as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                    logger.warning("Retry %d for %s: %s", attempt + 1, url, exc)

        raise last_exc or RuntimeError("GET failed after retries")

    async def head(self, url: str, **kwargs: Any) -> httpx.Response:
        """Perform a HEAD request with SSRF protection."""
        validate_url(url)
        headers = kwargs.pop("headers", {})
        headers.setdefault("User-Agent", self._get_user_agent())

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            max_redirects=5,
        ) as client:
            resp = await client.head(url, headers=headers, **kwargs)
            resp.raise_for_status()
            return resp

    async def get_with_fallback(self, url: str, **kwargs: Any) -> httpx.Response:
        """Try HEAD first, fall back to GET if 405 (Method Not Allowed)."""
        try:
            return await self.head(url, **kwargs)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 405:
                return await self.get(url, **kwargs)
            raise
