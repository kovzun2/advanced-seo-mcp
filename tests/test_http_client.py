"""Tests for SafeHTTPClient — SSRF protection, retry, rate limiting."""

import asyncio

import httpx
import pytest
import respx

from advanced_seo_mcp.http_client import (
    SafeHTTPClient,
    RateLimiter,
    SSRFError,
    validate_url,
)


def test_ssrf_blocks_private_ip():
    with pytest.raises(SSRFError):
        validate_url("http://127.0.0.1/admin")
    with pytest.raises(SSRFError):
        validate_url("http://192.168.1.1/secret")
    with pytest.raises(SSRFError):
        validate_url("http://localhost:6379/FLUSHDB")


def test_ssrf_blocks_non_http_scheme():
    with pytest.raises(SSRFError):
        validate_url("file:///etc/passwd")
    with pytest.raises(SSRFError):
        validate_url("ftp://example.com/file")


def test_ssrf_allows_public_urls():
    # Should not raise
    validate_url("https://example.com/page")
    validate_url("http://example.com")


@respx.mock
@pytest.mark.anyio
async def test_retry_on_failure():
    """Client retries 3 times before giving up."""
    route = respx.get("https://example.com/test")
    route.side_effect = httpx.ConnectError("Connection refused")

    client = SafeHTTPClient(max_retries=3)
    with pytest.raises(httpx.ConnectError):
        await client.get("https://example.com/test")

    assert route.call_count == 3


@respx.mock
@pytest.mark.anyio
async def test_successful_response():
    respx.get("https://example.com/ok").mock(
        return_value=httpx.Response(200, text="OK")
    )
    client = SafeHTTPClient(max_retries=1)
    resp = await client.get("https://example.com/ok")
    assert resp.status_code == 200
    assert resp.text == "OK"


@respx.mock
@pytest.mark.anyio
async def test_head_fallback_on_405():
    respx.head("https://example.com/check").mock(return_value=httpx.Response(405))
    respx.get("https://example.com/check").mock(
        return_value=httpx.Response(200, text="OK")
    )
    client = SafeHTTPClient(max_retries=1)
    resp = await client.get_with_fallback("https://example.com/check")
    assert resp.status_code == 200


def test_rate_limiter_delays():
    """Rate limiter should delay consecutive calls."""
    limiter = RateLimiter(calls_per_second=100)  # 10ms interval
    start = asyncio.get_event_loop().time()

    async def test():
        await limiter.acquire()
        await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start
        # Should have waited at least ~10ms
        assert elapsed >= 0.005

    asyncio.run(test())
