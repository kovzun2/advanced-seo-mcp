"""Tests for technical_auditor provider."""

import respx
import httpx
import pytest

from advanced_seo_mcp.providers.technical_auditor import TechnicalAuditor
from advanced_seo_mcp.http_client import SafeHTTPClient
from advanced_seo_mcp.models.technical import TechnicalAudit


@pytest.fixture
def http_client() -> SafeHTTPClient:
    return SafeHTTPClient(max_retries=1)


@pytest.fixture
def auditor(http_client: SafeHTTPClient) -> TechnicalAuditor:
    return TechnicalAuditor(http_client)


@respx.mock
@pytest.mark.anyio
async def test_technical_audit_all_good(auditor: TechnicalAuditor):
    base = "https://example.com"
    respx.head(f"{base}/").mock(
        return_value=httpx.Response(
            200,
            headers={
                "Strict-Transport-Security": "max-age=31536000",
                "X-Frame-Options": "DENY",
                "X-Content-Type-Options": "nosniff",
            },
        )
    )
    respx.get(f"{base}/robots.txt").mock(
        return_value=httpx.Response(200, text="User-agent: *\nAllow: /")
    )
    respx.head(f"{base}/sitemap.xml").mock(return_value=httpx.Response(200))

    result = await auditor.analyze(base)
    assert isinstance(result, TechnicalAudit)
    assert result.domain == "example.com"
    assert result.has_robots_txt is True
    assert result.has_sitemap is True
    assert result.https_enabled is True
    assert result.hsts_enabled is True
    assert 0 <= result.score <= 100


@respx.mock
@pytest.mark.anyio
async def test_technical_audit_missing_files(http_client: SafeHTTPClient):
    auditor = TechnicalAuditor(http_client)
    base = "https://example.com"
    respx.head(f"{base}/").mock(return_value=httpx.Response(200, headers={}))
    respx.get(f"{base}/robots.txt").mock(return_value=httpx.Response(404))
    respx.head(f"{base}/sitemap.xml").mock(return_value=httpx.Response(404))
    respx.head(f"{base}/sitemap_index.xml").mock(return_value=httpx.Response(404))
    respx.head(f"{base}/wp-sitemap.xml").mock(return_value=httpx.Response(404))

    result = await auditor.analyze(base)
    assert result.has_robots_txt is False
    assert result.has_sitemap is False
    assert result.hsts_enabled is False
    assert result.score < 80
