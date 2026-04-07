"""Tests for content_analyzer provider."""

import respx
import httpx
import pytest

from advanced_seo_mcp.providers.content_analyzer import ContentAnalyzer
from advanced_seo_mcp.http_client import SafeHTTPClient


@pytest.fixture
def http_client() -> SafeHTTPClient:
    return SafeHTTPClient(max_retries=1)


@pytest.fixture
def analyzer(http_client: SafeHTTPClient) -> ContentAnalyzer:
    return ContentAnalyzer(http_client)


@respx.mock
@pytest.mark.anyio
async def test_keyword_density(analyzer: ContentAnalyzer):
    html = "<html><body><p>python programming python coding python development</p></body></html>"
    respx.get("https://example.com/page").mock(return_value=httpx.Response(200, text=html))
    result = await analyzer.analyze("https://example.com/page", target_keyword="python")
    assert result["target_analysis"] is not None
    assert result["target_analysis"]["keyword"] == "python"
    assert result["target_analysis"]["count"] == 3
