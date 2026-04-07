"""Tests for link_inspector provider."""

import respx
import httpx
import pytest

from advanced_seo_mcp.providers.link_inspector import LinkInspector
from advanced_seo_mcp.http_client import SafeHTTPClient


@pytest.fixture
def http_client() -> SafeHTTPClient:
    return SafeHTTPClient(max_retries=1)


@pytest.fixture
def inspector(http_client: SafeHTTPClient) -> LinkInspector:
    return LinkInspector(http_client)


@respx.mock
@pytest.mark.anyio
async def test_broken_links(inspector: LinkInspector):
    page_html = """
    <html><body>
    <a href="https://example.com/ok">OK Link</a>
    <a href="https://example.com/broken">Broken Link</a>
    </body></html>
    """
    respx.get("https://example.com/page").mock(
        return_value=httpx.Response(200, text=page_html)
    )
    respx.head("https://example.com/ok").mock(return_value=httpx.Response(200))
    respx.head("https://example.com/broken").mock(return_value=httpx.Response(404))

    result = await inspector.analyze("https://example.com/page", limit=10)
    assert result["broken_count"] == 1
    assert result["working_count"] == 1
    assert result["total_scanned"] == 2
