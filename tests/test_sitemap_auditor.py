"""Tests for sitemap_auditor provider."""

import respx
import httpx
import pytest

from advanced_seo_mcp.providers.sitemap_auditor import SitemapAuditor
from advanced_seo_mcp.http_client import SafeHTTPClient


@pytest.fixture
def http_client() -> SafeHTTPClient:
    return SafeHTTPClient(max_retries=1)


@pytest.fixture
def auditor(http_client: SafeHTTPClient) -> SitemapAuditor:
    return SitemapAuditor(http_client)


@respx.mock
@pytest.mark.anyio
async def test_sitemap_no_sitemap(auditor: SitemapAuditor):
    respx.get("https://example.com/sitemap.xml").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/sitemap_index.xml").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/wp-sitemap.xml").mock(return_value=httpx.Response(404))
    result = await auditor.analyze("https://example.com", limit=2)
    assert "error" in result


@respx.mock
@pytest.mark.anyio
async def test_sitemap_found(auditor: SitemapAuditor):
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://example.com/page1</loc></url>
        <url><loc>https://example.com/page2</loc></url>
    </urlset>'''
    respx.get("https://example.com/sitemap.xml").mock(return_value=httpx.Response(200, text=sitemap_xml))
    respx.get("https://example.com/page1").mock(return_value=httpx.Response(200, text="<html><body><h1>Test</h1></body></html>"))
    result = await auditor.analyze("https://example.com", limit=1)
    assert "error" not in result
    assert result["total_in_sitemap"] == 2
